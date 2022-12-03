import docplex.mp.solution
from docplex.mp.conflict_refiner import ConflictRefiner
from docplex.mp.model import Model as CplexModel

from ..data import Parameters, Item, Store
from . import Variables, set_objective, set_constraints


class Model:
    mdl: CplexModel
    parameters: Parameters
    variables: Variables

    def __init__(self, parameters: Parameters):
        self.parameters = parameters

    def create(self, initial_store_inventories: dict[tuple[Item, Store], int],
                 initial_factory_inventories: dict[Item, int]):
        self.mdl = CplexModel()
        self.variables = Variables(self.parameters, self.mdl, initial_store_inventories, initial_factory_inventories)
        set_constraints(self.mdl, self.variables, self.parameters)
        set_objective(self.mdl, self.variables, self.parameters)

    def solve(self):
        self.mdl.export_as_lp("model.lp")
        self.mdl.set_time_limit(50)
        self.mdl.solve(log_output=True)
        print(self.mdl.solve_status)

        crr = ConflictRefiner().refine_conflict(self.mdl, display=True)
        crr.display()

        #self.mdl.print_solution()

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

        return solution

    def clear(self):
        self.mdl.clear()
