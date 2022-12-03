import logging

from . import Store, Item
import numpy as np


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
                           price={p: np.random.uniform(0, 10) for p in self.periods},
                           production_cost={p: np.random.uniform(0, 10) for p in self.periods},
                           holding_cost={p: np.random.uniform(0, 10) for p in self.periods},
                           hauling_cost={p: np.random.uniform(0, 10) for p in self.periods},
                           production_setup_cost={p: np.random.uniform(0, 10) for p in self.periods})
                      for i in range(self.num_items)]

    def __generate_stores(self):
        self.stores = [Store(id=i,
                             store_capacity=np.random.uniform(1000000, 100000000),
                             hauled_item_limit={p: np.random.uniform(0, 10) for p in self.periods},
                             order_renewal_cost={p: np.random.uniform(0, 10) for p in self.periods},
                             renewal_cost={item: {p: np.random.uniform(0, 10) for p in self.periods}
                                           for item in self.items},
                             holding_cost={item: {p: np.random.uniform(0, 10) for p in self.periods}
                                           for item in self.items})
                       for i in range(self.num_stores)]

    def generate_data(self):
        self.__generate_items()
        self.logger.info("Items are generated")
        self.__generate_stores()
        self.logger.info("Stores are generated")

        self.production_capacity = {t: np.random.uniform(1000000, 100000000) for t in self.periods}
        self.renewal_limit = {t: np.random.uniform(10000000, 100000000) for t in self.periods}

        self.u = list(np.linspace(0, 3000, num=3))
        d_ranges = list(np.linspace(0, 3000, num=4))

        self.d = []
        for index in range(len(d_ranges) - 1):
            first = d_ranges[index]
            second = d_ranges[index + 1]

            self.d.append(np.random.uniform(first, second))
