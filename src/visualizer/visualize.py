import numpy as np
import pandas as pd
import streamlit.config_option

from . import plt

def inventories_at_time(solution: dict[str, pd.DataFrame], stores: list[int], period: int):
    inventories_before_renewal = solution["inventory_store"]
    inventories_after_renewal = solution["inventory_after_renewal"]

    items_I = inventories_before_renewal["item"].values
    stores_I = inventories_before_renewal["store"].values
    periods_I = inventories_before_renewal["period"].values
    inventories_I = inventories_before_renewal["inventory"].values

    items_U = inventories_after_renewal["item"].values
    stores_U = inventories_after_renewal["store"].values
    periods_U = inventories_after_renewal["period"].values
    inventories_U = inventories_after_renewal["inventory"].values

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    ax.set_xticks(stores)
    ax.set_xticklabels([f"Store {m}" for m in stores])
    ax.set_ylabel("Inventory levels")

    width = 0.3
    starting_inv_bar = ax.bar(np.array(stores) - width,
                              [np.sum(inventories_I[np.logical_and(stores_I == store, periods_I == period - 1)])
                               for store in stores], width=width,
                              color="tab:blue")
    after_renewal_bar = ax.bar(np.array(stores),
                               [np.sum(inventories_U[np.logical_and(stores_U == store, periods_U == period)])
                                for store in stores], width=width,
                               color="tab:cyan")
    end_inv_bar = ax.bar(np.array(stores) + width,
                         [np.sum(inventories_I[np.logical_and(stores_I == store, periods_I == period)])
                          for store in stores], width=width, color="tab:orange")

    ax.legend((starting_inv_bar[0], after_renewal_bar[0], end_inv_bar[0]),
              ("Starting inventory", "After renewal", "Ending inventory"))

    return fig


def inventories_for_store(solution: dict[str, pd.DataFrame], store, periods: list[int], items: list[int]):
    inventories_before_renewal = solution["inventory_store"]
    inventories_after_renewal = solution["inventory_after_renewal"]

    items_I = inventories_before_renewal["item"].values
    stores_I = inventories_before_renewal["store"].values
    periods_I = inventories_before_renewal["period"].values
    inventories_I = inventories_before_renewal["inventory"].values

    items_U = inventories_after_renewal["item"].values
    stores_U = inventories_after_renewal["store"].values
    periods_U = inventories_after_renewal["period"].values
    inventories_U = inventories_after_renewal["inventory"].values

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    ax.set_xticks(periods)
    ax.set_xticklabels([f"Period {t}" for t in periods], rotation=45)
    ax.set_ylabel("Inventory levels")

    width = 0.3
    starting_inv_bar = ax.bar(np.array(periods) - width,
                              [np.sum(inventories_I[
                                          np.logical_and(np.logical_and(stores_I == store, periods_I == period - 1),
                                                         np.isin(items_I, items))])
                               for period in periods], width=width,
                              color="tab:blue")
    after_renewal_bar = ax.bar(np.array(periods),
                               [np.sum(inventories_U[
                                           np.logical_and(np.logical_and(stores_U == store, periods_U == period),
                                                          np.isin(items_U, items))])
                                for period in periods], width=width,
                               color="tab:cyan")
    end_inv_bar = ax.bar(np.array(periods) + width,
                         [np.sum(inventories_I[np.logical_and(np.logical_and(stores_I == store, periods_I == period),
                                                              np.isin(items_I, items))])
                          for period in periods], width=width, color="tab:orange")

    ax.legend((starting_inv_bar[0], after_renewal_bar[0], end_inv_bar[0]),
              ("Incoming Inventory", "After Order Arrival", "Ending inventory"))

    total_demands_for_items = {item: np.sum(solution["demand"]["demand"].values[solution["demand"]["store"] == store])
                               for item in solution["demand"]["item"].unique()}

    return fig


def inventory_stats(solution: dict[str, pd.DataFrame], store: int):
    inventories_before_renewal = solution["inventory_store"]
    inventories_after_renewal = solution["inventory_after_renewal"]

    def get_id(x):
        return x.id

    get_id_v = np.vectorize(get_id)

    items_I = get_id_v(inventories_before_renewal["item"].values)
    stores_I = get_id_v(inventories_before_renewal["store"].values)
    periods_I = inventories_before_renewal["period"].values
    inventories_I = inventories_before_renewal["inventory"].values

    items_U = get_id_v(inventories_after_renewal["item"].values)
    stores_U = get_id_v(inventories_after_renewal["store"].values)
    periods_U = inventories_after_renewal["period"].values
    inventories_U = inventories_after_renewal["inventory"].values

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    ax.plot(np.unique(periods_I), [np.sum(inventories_I[np.logical_and(stores_I == store, periods_I == period - 1)])
                                   for period in np.unique(periods_I)])

    return fig


def top_n_demand(solution: dict[str, pd.DataFrame], n_top, width=None, color="tab:blue"):
    demand = solution["demand"]["demand"].values
    items = solution["demand"]["item"].values
    stores = solution["demand"]["store"].values
    periods = solution["demand"]["period"].values

    demands = {(store, period): np.sum(demand[np.logical_and(stores == store, periods == period)])
               for store in np.unique(stores) for period in np.unique(periods)}

    demands = dict(sorted(demands.items(), key=lambda item: item[1], reverse=True))

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    ax.set_title(f"Top {n_top} Average Demand Levels", fontsize=20)

    if width is not None:
        fig.set_figwidth(width)

    x_axes = [f"Store {store} \n Period {period}" for store, period in demands.keys()]
    ax.bar(x_axes[:n_top], list(demands.values())[:n_top], color=color)

    return fig


def top_n_remaining_inventories(solution: dict[str, pd.DataFrame], n_top, width=None, color="tab:blue"):
    inventory = solution["inventory_store"]["inventory"].values
    items = solution["inventory_store"]["item"].values
    stores = solution["inventory_store"]["store"].values
    periods = solution["inventory_store"]["period"].values

    inventories = {(store, period): np.sum(inventory[np.logical_and(stores == store, periods == period)])
                   for store in np.unique(stores) for period in np.unique(periods)}

    inventories = dict(sorted(inventories.items(), key=lambda item: item[1], reverse=True))

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    ax.set_title(f"Top {n_top} Inventories Levels", fontsize=20)

    if width is not None:
        fig.set_figwidth(width)

    x_axes = [f"Store {store} \n Period {period}" for store, period in inventories.keys()]
    ax.bar(x_axes[:n_top], list(inventories.values())[:n_top], color=color)

    return fig


def top_n_produced_item_averages(solution: dict[str, pd.DataFrame], n_top, width=None, color="tab:blue"):
    production = solution["production"]["production"].values
    items = solution["production"]["item"].values
    periods = solution["production"]["period"].values

    productions = {item: 0 if len(production[items == item]) == 0
    else np.mean(production[items == item])
                   for item in np.unique(items)}

    productions = dict(sorted(productions.items(), key=lambda item: item[1], reverse=True))

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    ax.set_title(f"Top {n_top} Average Item Production", fontsize=20)

    if width is not None:
        fig.set_figwidth(width)

    x_axes = [f"Item {item}" for item in productions.keys()]
    ax.bar(x_axes[:n_top], list(productions.values())[:n_top], color=color)

    return fig


def item_demand_pie_chart(solution: dict[str, pd.DataFrame], n_top):
    demand = solution["demand"]["demand"].values
    items = solution["demand"]["item"].values
    stores = solution["demand"]["store"].values
    periods = solution["demand"]["period"].values

    demands = {item: np.sum(demand[items == item])
               for item in np.unique(items)}

    demands = dict(sorted(demands.items(), key=lambda item: item[1], reverse=True))

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    ax.set_title(f"Overall demand of items", fontsize=20)

    pie_sizes = list(demands.values())[0: n_top] + [np.sum(list(demands.values())[n_top:])]
    pie_labels = [f"Item {item}" for item in list(demands.keys())[0: n_top]] + ["Other"]

    ax.pie(x=pie_sizes, labels=pie_labels)

    return fig


def plot_capacity(solution: dict[str, pd.DataFrame]):
    items = solution["production"]["item"].values
    periods = solution["production"]["period"].values
    productions = solution["production"]["production"].values

    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    production_line, = ax.plot(np.unique(periods), [np.sum(productions[periods == period]) for period in np.unique(periods)],
                               color="tab:blue", label="Production")

    ax.set_title("Production Over Periods", fontsize=20)
    ax.legend([production_line], ["Production"], loc="upper right",
              framealpha=1, facecolor='white', frameon=True)
    return fig