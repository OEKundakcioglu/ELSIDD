from . import Item, Store
import matplotlib.pyplot as plt


class Parameters:
    items: list[Item]
    stores: list[Store]
    periods: list[int]
    production_capacity: dict[int, int]
    renewal_limit: dict[int, int]
    u: list[float]
    d: list[float]

    def __init__(self, items: list[Item], stores: list[Store], periods: list[int], production_capacity: dict[int, int]
                 , renewal_limit: dict[int, int], u: list[float], d: list[float]):
        self.items = items
        self.stores = stores
        self.periods = periods
        self.production_capacity = production_capacity
        self.renewal_limit = renewal_limit
        self.u = u
        self.d = d

        self.plot_g_function()

    def plot_g_function(self):
        fig, ax = plt.subplots()
        fig: plt.Figure
        ax: plt.Axes

        ax.plot(self.u, self.d)
        ax.set_title("G function")
        ax.set_xlabel("u")
        ax.set_ylabel("d")

        plt.show()