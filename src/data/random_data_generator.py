import logging

import numpy as np

from . import Store, Item


class DataGenerator:
    logger = logging.getLogger("Data Generator")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    periods: list[int]
    items: list[Item]
    stores: list[Store]
    production_capacity: dict[int, int]
    renewal_limit: dict[int, int]
    u: list[float]
    d: list[float]

    def __init__(self, seed: int, num_items: int, num_stores: int, num_periods: int):
        np.random.seed(seed)
        self.num_items = num_items
        self.num_stores = num_stores
        self.periods = list(range(num_periods))

    def __generate_items(self):
        self.items = [Item(id=i,
                           price={p: np.random.uniform(2, 3) for p in self.periods},
                           production_cost={p: np.random.uniform(0.0001, 1) for p in self.periods},
                           holding_cost={p: np.random.uniform(0.0001, 1) for p in self.periods},
                           production_setup_cost={p: np.random.uniform(100, 300) for p in self.periods})
                      for i in range(self.num_items)]

    def __generate_stores(self):
        self.stores = [Store(id=i,
                             store_capacity=np.random.uniform(1000, 1000),
                             hauled_item_limit={p: np.random.uniform(1000, 1000) for p in self.periods},
                             order_renewal_cost={p: np.random.uniform(100, 300) for p in self.periods},
                             renewal_cost={item: {p: np.random.uniform(0.0001, 1) for p in self.periods}
                                           for item in self.items},
                             holding_cost={item: {p: np.random.uniform(0.0001, 1) for p in self.periods}
                                           for item in self.items})
                       for i in range(self.num_stores)]

    def __generate_demand_curve(self, n_segments=3):
        def _function(low, slope, U):
            return low + slope * U

        u_values = []
        d_values = []

        base_slope = np.random.uniform(0.6, 0.9)
        for slope in np.linspace(base_slope, 0, n_segments):
            if len(u_values) == 0:
                u_values.append(0)
                d_values.append(0)

            u_low = u_values[-1]
            u_high = u_low + np.random.uniform(10, 20)

            d_low = d_values[-1]
            d_high = _function(d_low, slope, u_high - u_low)

            u_values.append(u_high)
            d_values.append(d_high)

        self.u = u_values
        self.d = d_values

    def generate_data(self):
        self.__generate_items()
        self.logger.info("Items are generated")
        self.__generate_stores()
        self.logger.info("Stores are generated")
        self.__generate_demand_curve()
        self.logger.info("Demand curve is generated")

        self.production_capacity = {t: np.random.uniform(600, 1000) for t in self.periods}
        self.renewal_limit = {t: np.random.uniform(600, 1000) for t in self.periods}

    def __dict__(self):
        return {
            "items": [item.__dict__() for item in self.items],
            "stores": [store.__dict__() for store in self.stores],
            "periods": self.periods,
            "production_capacity": self.production_capacity,
            "renewal_limit": self.renewal_limit,
            "u": self.u,
            "d": self.d
        }

    def save_to_json(self, path):
        import json
        with open(path, "w") as f:
            json.dump(self.__dict__(), f)
