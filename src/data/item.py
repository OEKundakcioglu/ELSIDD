class Item:
    id: int
    price: dict[int, float]
    production_cost: dict[int, float]
    holding_cost: dict[int, float]
    production_setup_cost: dict[int, float]

    def __init__(self, id: int, price: dict[int, float], production_cost: dict[int, float],
                 holding_cost: dict[int, float],
                 production_setup_cost: dict[int, float]):
        self.id = id
        self.price = price
        self.production_cost = production_cost
        self.holding_cost = holding_cost
        self.production_setup_cost = production_setup_cost

    def __hash__(self):
        return self.id

    def __str__(self):
        return f"{self.id}"

    def __dict__(self):
        return {
            "id": self.id,
            "price": self.price,
            "production_cost": self.production_cost,
            "holding_cost": self.holding_cost,
            "production_setup_cost": self.production_setup_cost
        }
