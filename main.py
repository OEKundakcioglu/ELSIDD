from tubitak.data import Parameters, DataGenerator
from tubitak.model import Model
from tubitak.simple_heuristic import SimpleHeuristic

if __name__ == "__main__":
    data_generator = DataGenerator(seed=1, num_items=100, num_stores=10, num_periods=10)
    data_generator.generate_data()

    parameters = Parameters(data_generator.items, data_generator.stores, data_generator.periods
                            , data_generator.production_capacity, data_generator.renewal_limit,
                            data_generator.u, data_generator.d)

    simple_heuristic = SimpleHeuristic(parameters, n_decomposition=2)
    simple_heuristic.decompose_problem()
    simple_heuristic.solve()

    """
    model = Model(parameters)
    initial_store_inventories = {(item, store): 0 for item in parameters.items for store in parameters.stores}
    initial_factory_inventories = {item: 0 for item in parameters.items}
    model.create(initial_store_inventories, initial_factory_inventories)
    model.solve()

    solution = model.get_solution()
    """

