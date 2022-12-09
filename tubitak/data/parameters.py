import logging

import matplotlib.pyplot as plt
import streamlit as st

from . import Item, Store


class Parameters:
    items: list[Item]
    stores: list[Store]
    periods: list[int]
    production_capacity: dict[int, int]
    renewal_limit: dict[int, int]
    u: list[float]
    d: list[float]
    logger = logging.getLogger("Parameters")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    def __init__(self, items=None, stores=None, periods=None, production_capacity=None, renewal_limit=None,
                 u=None, d=None, path=None, file=None):
        if path is not None or file is not None:
            with st.spinner("Loading parameters..."):
                self.__load(path=path, file=file)
                st.success("Parameters loaded successfully")
        else:
            self.items = items
            self.stores = stores
            self.periods = periods
            self.production_capacity = production_capacity
            self.renewal_limit = renewal_limit
            self.u = u
            self.d = d

        self.plot_g_function()

    def __load(self, path=None, file=None):
        import json
        self.items = []
        self.stores = []
        self.periods = []

        if file is None:
            with open(path, "r") as f:
                data = json.load(f)

        else:
            data = json.load(file)

        for item in data["items"]:
            item = Item(id=int(item["id"]),
                        price={int(p): float(price) for p, price in item["price"].items()},
                        production_cost={int(p): float(cost) for p, cost in item["production_cost"].items()},
                        holding_cost={int(p): float(cost) for p, cost in item["holding_cost"].items()},
                        production_setup_cost={int(p): float(cost) for p, cost in
                                               item["production_setup_cost"].items()})
            self.items.append(item)

        for store in data["stores"]:
            renewal_cost = {}
            holding_cost = {}
            for item_id in store["renewal_cost"]:
                if len([item for item in self.items if item.id == int(item_id)]) > 0:
                    item = [item for item in self.items if item.id == int(item_id)][0]
                else:
                    self.logger.warning(f"Item with id {item_id} not found")
                    continue

                renewal_cost[item] = {int(p): float(cost) for p, cost in store["renewal_cost"][item_id].items()}
                holding_cost[item] = {int(p): float(cost) for p, cost in store["holding_cost"][item_id].items()}

            self.stores.append(Store(id=int(store["id"]),
                                     order_renewal_cost={int(p): float(cost) for p, cost in
                                                         store["order_renewal_cost"].items()},
                                     store_capacity=int(store["store_capacity"]),
                                     hauled_item_limit={int(p): float(limit) for p, limit in
                                                        store["hauled_item_limit"].items()},
                                     renewal_cost=renewal_cost,
                                     holding_cost=holding_cost))

        self.periods = [int(p) for p in data["periods"]]
        self.production_capacity = {int(p): int(capacity) for p, capacity in data["production_capacity"].items()}
        self.renewal_limit = {int(p): int(limit) for p, limit in data["renewal_limit"].items()}
        self.u = [float(u) for u in data["u"]]
        self.d = [float(d) for d in data["d"]]

        self.logger.info(f"Loaded parameters from {path}")
        st.text(f"Loaded parameters from {path}")

    def plot_g_function(self):
        fig, ax = plt.subplots()
        fig: plt.Figure
        ax: plt.Axes

        ax.plot(self.u, self.d)
        ax.set_title("G function")
        ax.set_xlabel("u")
        ax.set_ylabel("d")

        plt.show()
