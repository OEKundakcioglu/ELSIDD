import json

import numpy as np
import pandas as pd
from docplex.mp.conflict_refiner import ConflictRefiner
from docplex.mp.model import Model as CplexModel

from . import Variables, set_objective, set_constraints
from ..data import Parameters, Item, Store


class Model:
    mdl: CplexModel
    parameters: Parameters
    variables: Variables

    def __init__(self, parameters: Parameters):
        self.parameters = parameters

    def create(self, initial_store_inventories: dict[tuple[Item, Store, int], int],
               initial_factory_inventories: dict[tuple[Item, int], int]):
        self.mdl = CplexModel()
        self.variables = Variables(self.parameters, self.mdl, initial_store_inventories, initial_factory_inventories)
        set_constraints(self.mdl, self.variables, self.parameters)
        set_objective(self.mdl, self.variables, self.parameters)

    def solve(self, time_limit):
        self.mdl.set_time_limit(time_limit)

        self.mdl.export_as_lp("model.lp")

        self.mdl.solve(log_output=True)

        crr = ConflictRefiner().refine_conflict(self.mdl, display=True)
        crr.display()

        print(self.mdl.solution.solve_status)

        # self.mdl.print_solution()

    def get_solution(self):
        solution = {}
        solution["D"]: dict[tuple[Item, Store, int]] = {}
        for key, var in self.variables.D.items():
            solution["D"][key] = self.mdl.solution.get_value(var)

        solution["I"]: dict[tuple[Item, Store, int]] = {}
        for key, var in self.variables.I.items():
            solution["I"][key] = self.mdl.solution.get_value(var)

        solution["I_total"]: dict[tuple[Item, int]] = {}
        for key, var in self.variables.I_total.items():
            solution["I_total"][key] = self.mdl.solution.get_value(var)

        solution["x"]: dict[tuple[Item, int]] = {}
        for key, var in self.variables.x.items():
            solution["x"][key] = self.mdl.solution.get_value(var)

        solution["z"]: dict[tuple[Item, Store, int]] = {}
        for key, var in self.variables.z.items():
            solution["z"][key] = self.mdl.solution.get_value(var)

        solution["Z"]: dict[tuple[Store, int]] = {}
        for key, var in self.variables.Z.items():
            solution["Z"][key] = self.mdl.solution.get_value(var)

        solution["U"]: dict[tuple[Item, Store, int]] = {}
        for key, var in self.variables.U.items():
            solution["U"][key] = self.mdl.solution.get_value(var)

        solution["x_binary"]: dict[tuple[Item, int]] = {}
        for key, var in self.variables.x_binary.items():
            solution["x_binary"][key] = self.mdl.solution.get_value(var)

        solution["Z_binary"]: dict[tuple[Item, Store, int]] = {}
        for key, var in self.variables.Z_binary.items():
            solution["Z_binary"][key] = self.mdl.solution.get_value(var)

        solution["revenue"] = self.mdl.solution.get_objective_value()

        return solution

    def clear(self):
        self.mdl.clear()

    def get_solution_as_dict_dataframe(self):
        data = {}

        solution = self.get_solution()

        for key, value in solution.items():
            if key == "I":
                key = "inventory_store"
                columns = ["item", "store", "period", "inventory"]
            elif key == "I_total":
                key = "inventory_total"
                columns = ["item", "period", "inventory"]
            elif key == "x":
                key = "production"
                columns = ["item", "period", "production"]
            elif key == "z":
                key = "renewal"
                columns = ["item", "store", "period", "renewal"]
            elif key == "Z":
                key = "renewal_total"
                columns = ["item", "period", "renewal"]
            elif key == "D":
                key = "demand"
                columns = ["item", "store", "period", "demand"]
            elif key == "U":
                key = "inventory_after_renewal"
                columns = ["item", "store", "period", "inventory"]
            elif key == "x_binary":
                continue
            elif key == "Z_binary":
                continue
            elif key == "revenue":
                continue
            else:
                raise ValueError("Unknown key")

            df = pd.Series(data=value).reset_index()
            df.columns = columns
            data[key] = df

        return self.__convert_objects_to_ids(data)

    def __convert_objects_to_ids(self, solution: dict):
        def get_id(x):
            return x.id

        get_id_v = np.vectorize(get_id)
        for key, df in solution.items():
            if "item" in df.columns:
                df["item"] = get_id_v(df["item"].values)
            if "store" in df.columns:
                df["store"] = get_id_v(df["store"].values)

        return solution

    def export_solution_to_json(self, path):
        temp_solution = {}
        for key1, value1 in self.get_solution().items():
            if key1 == "revenue":
                if key1 not in temp_solution:
                    temp_solution[key1] = 0
                temp_solution[key1] += value1
                continue

            temp_solution[key1] = []
            for key2, value2 in value1.items():
                variable_dict = {}
                for index, dimension in enumerate(key2):
                    if type(dimension) != int:
                        variable_dict[f"dim{index}"] = dimension.id
                    else:
                        variable_dict[f"dim{index}"] = dimension

                variable_dict["value"] = value2
                temp_solution[key1].append(variable_dict)

        solution_dict = {
            "number_of_items": len(self.parameters.items),
            "number_of_stores": len(self.parameters.stores),
            "number_of_periods": len(self.parameters.periods),
            "solution": temp_solution
        }

        with open(path, "w") as f:
            json.dump(solution_dict, f)

        return solution_dict
