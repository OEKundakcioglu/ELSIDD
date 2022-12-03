from logging import Logger

import numpy as np

from . import Parameters, Model

class SimpleHeuristic:
    n_decomposition: int
    parameters: Parameters
    start_periods: list[int]
    __logger = Logger("Simpler Heuristic")
    solutions: list[dict]

    def __init__(self, parameters: Parameters, n_decomposition=2):
        self.n_decomposition = n_decomposition
        self.parameters = parameters

    def decompose_problem(self) -> list[Parameters]:
        decomposed_periods = np.array_split(self.parameters.periods, self.n_decomposition)

        sub_problems = [self.__get_problem_for_period(periods) for periods in decomposed_periods]

        return sub_problems

    def __get_problem_for_period(self, periods: list[int]) -> Parameters:
        sub_parameters = Parameters(self.parameters.items, self.parameters.stores, self.parameters.periods[periods[0]:periods[-1]+1],
                                    self.parameters.production_capacity, self.parameters.renewal_limit,
                                    self.parameters.u, self.parameters.d)
        return sub_parameters

    def solve(self):
        sub_problems = self.decompose_problem()

        solutions = []
        for sub_problem in sub_problems:
            if len(solutions) == 0:
                initial_store_inventories = {(item, store, sub_problem.periods[0]-1): 0 for item in sub_problem.items for store in
                                             sub_problem.stores}
                initial_factory_inventories = {(item, sub_problem.periods[0]-1): 0 for item in sub_problem.items}

            else:
                initial_store_inventories = {key: value for key, value in solutions[-1]["I"].items() if sub_problem.periods[0]-1 in key}
                initial_factory_inventories = {key: value for key, value in solutions[-1]["I_total"].items() if sub_problem.periods[0]-1 in key}

            model = Model(sub_problem)
            model.create(initial_store_inventories, initial_factory_inventories)
            model.solve()
            solutions.append(model.get_solution())
            model.clear()

        self.solutions = solutions
        return solutions
