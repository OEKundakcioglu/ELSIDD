import logging
from logging import Logger

from docplex.mp.model import Model

from . import Variables
from ..data import Parameters

logger = logging.getLogger("Constraints")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

def set_constraints(mdl: Model, variables: Variables, parameters: Parameters):
    set_const1(mdl, variables, parameters)
    logger.info("const1 is set")
    set_const2(mdl, variables, parameters)
    logger.info("const2 is set")
    set_const3(mdl, variables, parameters)
    logger.info("const3 is set")
    set_const4(mdl, variables, parameters)
    logger.info("const4 is set")
    set_const5(mdl, variables, parameters)
    logger.info("const5 is set")
    set_const6(mdl, variables, parameters)
    logger.info("const6 is set")
    set_const7(mdl, variables, parameters)
    logger.info("const7 is set")
    set_const8(mdl, variables, parameters)
    logger.info("const8 is set")


def set_const1(mdl: Model, variables: Variables, parameters: Parameters):
    for i in parameters.items:
        for t in parameters.periods:
            mdl.add_constraint(variables.I_total[i, t-1] + variables.x[i, t] ==
                               variables.I_total[i, t] + mdl.sum(variables.z[i, m, t] for m in parameters.stores),
                               ctname=f"const1_{i.id}_{t}")


def set_const2(mdl: Model, variables: Variables, parameters: Parameters):
    for i in parameters.items:
        for m in parameters.stores:
            for t in parameters.periods:
                mdl.add_constraint(variables.I[i, m, t-1] + variables.z[i, m, t] ==
                                   variables.D[i, m, t] + variables.I[i, m, t],
                                   ctname=f"const2_{i.id}_{m.id}_{t}")


def set_const3(mdl: Model, variables: Variables, parameters: Parameters):
    for i in parameters.items:
        for m in parameters.stores:
            for t in parameters.periods:
                mdl.add_constraint(variables.U[i, m, t] ==
                                   variables.I[i, m, t-1] + variables.z[i, m, t],
                                   ctname=f"const3_{i.id}_{m.id}_{t}")


def set_const4(mdl: Model, variables: Variables, parameters: Parameters):
    for i in parameters.items:
        for m in parameters.stores:
            for t in parameters.periods:
                lambdas = mdl.continuous_var_list(keys=len(parameters.u), lb=0, name=f"lambda_{i.id}_{m.id}_{t}")
                y = mdl.binary_var_list(keys=len(parameters.u) - 1, name=f"y_{i.id}_{m.id}_{t}")

                mdl.add_constraint(variables.D[i, m, t] ==
                                   mdl.sum(lambdas[j] * parameters.d[j] for j in range(len(lambdas))),
                                   ctname=f"const4D_{i.id}_{m.id}_{t}")
                mdl.add_constraint(variables.U[i, m, t] ==
                                   mdl.sum(lambdas[j] * parameters.u[j] for j in range(len(lambdas))),
                                   ctname=f"const4U_{i.id}_{m.id}_{t}")

                mdl.add_constraint(mdl.sum(lambdas) == 1,
                                   ctname=f"const4sumLambda_{i.id}_{m.id}_{t}")

                mdl.add_constraint(mdl.sum(y) == 1,
                                   ctname=f"const4sumY_{i.id}_{m.id}_{t}")

                for j in range(len(lambdas)-1):
                    mdl.add_constraint(y[j] <= lambdas[j] + lambdas[j+1],
                                       ctname=f"const4range_{i.id}_{m.id}_{t}_{j}")


def set_const5(mdl: Model, variables: Variables, parameters: Parameters):
    for t in parameters.periods:
        mdl.add_constraint(mdl.sum(variables.x[i, t] for i in parameters.items) <=
                           parameters.production_capacity[t],
                           ctname=f"const5_{t}")


def set_const6(mdl: Model, variables: Variables, parameters: Parameters):
    for m in parameters.stores:
        for t in parameters.periods:
            mdl.add_constraint(mdl.sum(variables.U[i, m, t] for i in parameters.items) <=
                               m.store_capacity,
                               ctname=f"const6_{m.id}_{t}")


def set_const7(mdl: Model, variables: Variables, parameters: Parameters):
    for m in parameters.stores:
        for t in parameters.periods:
            mdl.add_constraint(variables.Z[m, t] ==
                               mdl.sum(variables.z[i, m, t] for i in parameters.items),
                               ctname=f"const7_{m.id}_{t}")


def set_const8(mdl: Model, variables: Variables, parameters: Parameters):
    for t in parameters.periods:
        mdl.add_constraint(mdl.sum(variables.Z[m, t] for m in parameters.stores) <=
                           parameters.renewal_limit[t],
                           ctname=f"const8_{t}")