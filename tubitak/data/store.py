from . import Item


class Store:
    id: int
    order_renewal_cost: dict[int, float]
    store_capacity: int
    hauled_item_limit: dict[int, float]
    renewal_cost: dict[Item, dict[int, float]]
    holding_cost: dict[Item, dict[int, float]]

    def __init__(self, id: int, order_renewal_cost: dict[int, float], store_capacity: int,
                 hauled_item_limit: dict[int, float], renewal_cost: dict[Item, dict[int, float]],
                 holding_cost: dict[Item, dict[int, float]]):
        self.id = id
        self.order_renewal_cost = order_renewal_cost
        self.store_capacity = store_capacity
        self.hauled_item_limit = hauled_item_limit
        self.renewal_cost = renewal_cost
        self.holding_cost = holding_cost

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.id)

    def __dict__(self):
        return {
            "id": self.id,
            "order_renewal_cost": self.order_renewal_cost,
            "store_capacity": self.store_capacity,
            "hauled_item_limit": self.hauled_item_limit,
            "renewal_cost": {item.id: self.renewal_cost[item] for item in self.renewal_cost},
            "holding_cost": {item.id: self.holding_cost[item] for item in self.holding_cost}
        }
