import logging

import numpy as np
import pandas as pd

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
                                           for item in self.items},
                             u={item: self.__generate_demand_curve(n_segments=3)[0] for item in self.items},
                             d={item: self.__generate_demand_curve(n_segments=3)[1] for item in self.items})
                       for i in range(self.num_stores)]

        for store in self.stores:
            store.d = {}
            store.u = {}

        self.get_demand("Talep _Fonksiyonu.csv")

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
            u_high = u_low + np.random.uniform(5, 5)

            d_low = d_values[-1]
            d_high = _function(d_low, slope, u_high - u_low)

            u_values.append(u_high)
            d_values.append(d_high)

        u_values.append(1e+4)
        d_values.append(d_values[-1])

        return u_values, d_values

    def generate_data(self):
        self.__generate_items()
        self.logger.info("Items are generated")
        self.__generate_stores()
        self.logger.info("Stores are generated")
        self.__generate_demand_curve()
        self.logger.info("Demand curve is generated")

        self.production_capacity = {t: np.random.uniform(1500, 1500) for t in self.periods}
        self.renewal_limit = {t: np.random.uniform(250, 250) for t in self.periods}

    def get_demand(self, path: str):
        df = pd.read_csv(path)
        slope_mapping = {}
        for index, row in df.iterrows():
            item = self.items[int(row["item"]) - 1]
            slopes = [0, float(row["5_10"]), float(row["10_15"]), float(row["15_20"])]
            slope_mapping[item] = slopes

        for store in self.stores:
            for item in self.items:
                store.u[item] = [0, 5, 10, 15, 20]
                store.d[item] = [0, 5]
                for i, slope in enumerate(slope_mapping[item]):
                    if i == 0:
                        continue
                    store.d[item].append(store.d[item][-1] + slope * 5)

                store.d[item].append(store.d[item][-1])
                store.u[item].append(1e+4)

    def __dict__(self):
        return {
            "items": [item.__dict__() for item in self.items],
            "stores": [store.__dict__() for store in self.stores],
            "periods": self.periods,
            "production_capacity": self.production_capacity,
            "renewal_limit": self.renewal_limit
        }

    def save_to_json(self, path):
        import json
        with open(path, "w") as f:
            json.dump(self.__dict__(), f)
