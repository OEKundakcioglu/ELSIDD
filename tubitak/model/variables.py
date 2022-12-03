import itertools
import logging

from docplex.mp.dvar import Var
from docplex.mp.model import Model

from ..data import Parameters, Item, Store


class Variables:
    x: dict[tuple[Item, int], Var]  # x[i, t] amount produced in period t of item i
    z: dict[tuple[Item, Store, int], Var]  # z[i, m, t] amount arrived in period t of item i to store m
    Z: dict[tuple[Store, int], Var]  # Z[m, t] total amount arrived in period t to store m
    D: dict[tuple[Item, Store, int], Var]  # D[i, m, t] amount demanded in period t of item i from store m
    U: dict[tuple[Item, Store, int], Var]  # U[i, m, t] amount left in period t of item i from store m after renewal
    I: dict[tuple[Item, Store, int], Var]  # I[i, m, t] left inventory of item i end of period t in store m
    I_total: dict[tuple[Item, int], Var]  # I[i, t] left inventory of item i end of period t in all stores

    x_binary: dict[tuple[Item, int], Var]  # 1 if x[i, t] > 0 else 0
    Z_binary: dict[tuple[Store, int], Var]  # 1 if z[i, m, t] > 0 else 0

    logger = logging.getLogger("Variables")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    def __init__(self, parameters: Parameters, mdl: Model, initial_store_inventories: dict[tuple[Item, Store, int], int],
                 initial_factory_inventories: dict[tuple[Item, int], int]):

        self.parameters = parameters

        self.x = mdl.continuous_var_dict(
            keys=list(itertools.product(parameters.items, parameters.periods)), lb=0, name="x")
        self.logger.info("Variable x is created")

        self.z = mdl.continuous_var_dict(
            keys=list(itertools.product(parameters.items, parameters.stores, parameters.periods)), lb=0,
            name="z")
        self.logger.info("Variable z is created")

        self.Z = mdl.continuous_var_dict(list(itertools.product(parameters.stores, parameters.periods)),
                                         lb=0, name="Z")
        self.logger.info("Variable Z is created")

        self.D = mdl.continuous_var_dict(
            list(itertools.product(parameters.items, parameters.stores, parameters.periods)), lb=0, name="D")
        self.logger.info("Variable D is created")

        self.U = mdl.continuous_var_dict(
            list(itertools.product(parameters.items, parameters.stores, parameters.periods)), lb=0, name="U")
        self.logger.info("Variable U is created")

        self.I = mdl.continuous_var_dict(
            list(itertools.product(parameters.items, parameters.stores, parameters.periods)), lb=0, name="I")
        self.logger.info("Variable I is created")

        self.I_total = mdl.continuous_var_dict(
            list(itertools.product(parameters.items, parameters.periods)), lb=0, name="I_total")
        self.logger.info("Variable I_total is created")

        self.x_binary = mdl.binary_var_dict(list(itertools.product(parameters.items, parameters.periods)),
                                            name="x_binary")
        self.logger.info("Variable x_binary is created")

        self.Z_binary = mdl.binary_var_dict(list(itertools.product(parameters.stores, parameters.periods)),
                                            name="Z_binary")
        self.logger.info("Variable Z_binary is created")

        for key, value in initial_store_inventories.items():
            self.I[key] = mdl.continuous_var(lb=value, ub=value, name=f"I_{key[0]}_{key[1]}_{key[2]}")

        for key, value in initial_factory_inventories.items():
            self.I_total[key] = mdl.continuous_var(lb=value, ub=value, name=f"I_total_{key[0]}_{key[1]}")

        self.logger.info("Variables are created")
