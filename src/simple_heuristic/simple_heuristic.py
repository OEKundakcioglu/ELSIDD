import json
from logging import Logger

import numpy as np
import pandas as pd
import streamlit as st

from . import Parameters, Model


class SimpleHeuristic:
    n_decomposition: int
    parameters: Parameters
    start_periods: list[int]
    __logger = Logger("Simpler Heuristic")
    solution_df: dict[str, pd.DataFrame]
    solution = {}
    revenue = 0

    def __init__(self, parameters: Parameters, n_decomposition=2):
        self.n_decomposition = n_decomposition
        self.parameters = parameters

    def decompose_problem(self) -> list[Parameters]:
        decomposed_periods = np.array_split(self.parameters.periods, self.n_decomposition)

        sub_problems = [self.__get_problem_for_period(periods) for periods in decomposed_periods]

        return sub_problems

    def __get_problem_for_period(self, periods: list[int]) -> Parameters:
        sub_parameters = Parameters(self.parameters.items, self.parameters.stores,
                                    self.parameters.periods[periods[0]:periods[-1] + 1],
                                    self.parameters.production_capacity, self.parameters.renewal_limit,
                                    self.parameters.u, self.parameters.d)
        return sub_parameters

    def solve(self, time_limit=50):
        sub_problems = self.decompose_problem()

        solution_dataframes = []
        solutions = []
        for index, sub_problem in enumerate(sub_problems):
            with st.spinner(f"Solving sub-problem {index + 1}..."):
                if len(solutions) == 0:
                    initial_store_inventories = {(item, store, sub_problem.periods[0] - 1): 0 for item in
                                                 sub_problem.items for store in
                                                 sub_problem.stores}
                    initial_factory_inventories = {(item, sub_problem.periods[0] - 1): 0 for item in sub_problem.items}

                else:
                    initial_store_inventories = {key: value for key, value in solutions[-1]["I"].items() if
                                                 sub_problem.periods[0] - 1 in key}
                    initial_factory_inventories = {key: value for key, value in solutions[-1]["I_total"].items() if
                                                   sub_problem.periods[0] - 1 in key}

                model = Model(sub_problem)
                model.create(initial_store_inventories, initial_factory_inventories)
                model.solve(time_limit)
                solution_dataframes.append(model.get_solution_as_dict_dataframe())
                solutions.append(model.get_solution())
                self.revenue += model.mdl.solution.get_objective_value()
                model.clear()

                st.success(f"Sub-problem {index + 1} solved successfully")

        solution = {}

        for key, value in solution_dataframes[0].items():
            solution[key] = pd.concat([solution_dict[key] for solution_dict in solution_dataframes], axis=0)

        for value in solutions:
            self.solution.update(value)

        self.solution_df = solution

    def import_solution_to_json(self, path):
        temp_solution = {}
        for key1, value1 in self.solution.items():
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
