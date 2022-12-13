import logging

import streamlit as st
from docplex.mp.model import Model

from . import Variables
from ..data import Parameters

logger = logging.getLogger("Objective")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


def set_objective(mdl: Model, variables: Variables, parameters: Parameters):
    placeholder = st.empty()
    with st.spinner("Setting objective..."):
        revenue = mdl.sum(i.price[t] * variables.D[i, m, t]
                          for i in parameters.items
                          for m in parameters.stores
                          for t in parameters.periods)

        fixed_production_cost = mdl.sum(i.production_setup_cost[t] * variables.x_binary[i, t]
                                        for i in parameters.items
                                        for t in parameters.periods)

        production_cost = mdl.sum(i.production_cost[t] * variables.x[i, t]
                                  for i in parameters.items
                                  for t in parameters.periods)

        holding_cost = mdl.sum(i.holding_cost[t] * variables.I_total[i, t]
                               for i in parameters.items
                               for t in parameters.periods)

        fixed_renewal_cost = mdl.sum(m.order_renewal_cost[t] * variables.Z_binary[m, t]
                                     for m in parameters.stores
                                     for t in parameters.periods)

        renewal_cost = mdl.sum(m.renewal_cost[i][t] * variables.z[i, m, t]
                               for i in parameters.items
                               for m in parameters.stores
                               for t in parameters.periods)

        holding_cost_store_specific = mdl.sum(m.holding_cost[i][t] * variables.z[i, m, t]
                                              for i in parameters.items
                                              for m in parameters.stores
                                              for t in parameters.periods)

        mdl.set_objective("max",
                          revenue - fixed_production_cost - production_cost - holding_cost - fixed_renewal_cost - renewal_cost -
                          holding_cost_store_specific)

        logger.info("Objective is set")
        placeholder.success("Objective is created")
        del placeholder
