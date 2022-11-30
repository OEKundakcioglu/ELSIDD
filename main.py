from problem_instance import DatasetGenerator
from trans_mip import heuristic_with_transportation

N, T, J = 10, 20, 3

data_generator = DatasetGenerator(N=N, T=T, J=J)
problem_instance = data_generator.load_data()

columns = heuristic_with_transportation(problem_instance, (N, T, J), )

