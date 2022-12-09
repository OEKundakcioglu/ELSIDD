from docplex.mp.model import Model


def heuristic_with_transportation(dataset, key, I_prod, I_store):
    try:
        N, T, J = key

        mdl = Model('heur')
        store_number = 5
        u_prime = {key: dataset["u"][key] for key in dataset["u"].keys() if key[2] > 0}
        store_index = {key: dataset["u"][key] for key in dataset["u"].keys() if key[2] <= store_number and key[2] > 0}
        C_truck = 1000
        # C_store=[1000,1000]
        C_store = [1000, 1000, 1000, 1000, 1000]
        # C_store=[500,500,500,500,500]
        y = mdl.binary_var_dict(dataset["c"].keys(), lb=0, name='y')
        x = mdl.continuous_var_dict(dataset["c"].keys(), lb=0, name='x')
        I = mdl.continuous_var_dict(dataset["h"].keys(), lb=0, name='I')
        I_prime = mdl.continuous_var_dict(dataset["h"].keys(), lb=0, name='I_prime')
        Y = mdl.continuous_var_dict(u_prime.keys(), lb=0, name='Y')
        U = mdl.continuous_var_dict(dataset["c"].keys(), lb=0, name="U")
        D = mdl.continuous_var_dict(dataset["c"].keys(), lb=0, name="D")
        z = mdl.binary_var_dict(u_prime.keys(), lb=0, name='z')
        alpha = mdl.continuous_var_dict(dataset["u"].keys(), lb=0, name="alpha")
        v = mdl.binary_var_dict(u_prime.keys(), name="v")
        # Y -> z

        for i, t in dataset["c"].keys():
            mdl.add_constraint(
                I[i, t - 1] + x[i, t] == I[i, t] + (mdl.sum(Y[i, t, s + 1] for s in range(store_number))),
                "cons1_i={},t={}".format(i, t))
            mdl.add_constraint(
                I_prime[i, t - 1] + (mdl.sum(Y[i, t, s + 1] for s in range(store_number))) == D[i, t] + I_prime[i, t],
                "cons2_i={},t={}".format(i, t))
            mdl.add_constraint(U[i, t] == I[i, t - 1] + (mdl.sum(Y[i, t, s + 1] for s in range(store_number))),
                               "cons3_i={},t={}".format(i, t))
            mdl.add_constraint(alpha[i, t, 0] <= v[i, t, 1], "cons4_i={},t={},j={}".format(i, t, 0))
            mdl.add_constraint(alpha[i, t, J] <= v[i, t, J], "cons5_i={},t={},j={}".format(i, t, J))
            mdl.add_constraint(mdl.sum(alpha[i, t, j] for j in range(J + 1)) == 1, "cons6_i={},t={}".format(i, t))
            mdl.add_constraint(mdl.sum(v[i, t, j] for j in range(1, J + 1)) == 1, "cons7_i={},t={}".format(i, t))
            mdl.add_constraint(
                U[i, t] == mdl.sum(alpha[i, t, j] * dataset["u"][i, t, j] for j in range(J + 1)),
                "cons8_i={},t={}".format(i, t))
            mdl.add_constraint(
                D[i, t] == mdl.sum(alpha[i, t, j] * dataset["d"][i, t, j] for j in range(J + 1)),
                "cons9_i={},t={}".format(i, t))
            mdl.add_constraint(x[i, t] <= 250000 * y[i, t], "cons15_i={},t={}".format(i, t))

        for i in range(1, N + 1):
            mdl.add_constraint(I[i, 0] == I_prod, "cons10_i={},t={}".format(i, 0))
            mdl.add_constraint(I_prime[i, 0] == I_store, "cons10_i={},t={}".format(i, 0))

        for i, t, j in u_prime.keys():
            mdl.add_constraint(alpha[i, t, j - 1] + alpha[i, t, j] <= 1, "cons11_i={},t={},j={}".format(i, t, j))
            if j != J:
                mdl.add_constraint(alpha[i, t, j] <= v[i, t, j] + v[i, t, j + 1],
                                   "cons12_i={},t={},j={}".format(i, t, j))
        """
        for t in range(1, T + 1):
         print( mdl.add_constraint((mdl.sum(Y[i, t,s+1] for s in range(store_number) for i in range(1, N + 1))) <= C_truck*(mdl.sum(z[i, t,s+1] for s in range(store_number) for i in range(1, N + 1))),"cons20_i={},t={},j={}".format(i, t, j)))
        """
        for i, t, s in store_index.keys():
            mdl.add_constraint((Y[i, t, s] <= C_truck * z[i, t, s]), "cons20_i={},t={},j={}".format(i, t, j))

        for s in range(len(C_store)):
            mdl.add_constraint(mdl.sum(Y[i, t, s + 1] for i in range(1, N + 1) for t in range(1, T + 1)) <= C_store[s],
                               "cons14_t={}".format(t))

        for t in range(1, T + 1):
            mdl.add_constraint(mdl.sum(x[i, t] for i in range(1, N + 1)) <= dataset["C"][t],
                               "cons3_t={}".format(t))

        revenue = mdl.sum(dataset["p"][i, t] * D[i, t] for i, t in dataset["c"].keys())
        var_cost = mdl.sum(dataset["c"][i, t] * x[i, t] for i, t in dataset["c"].keys())
        trans_cost = mdl.sum(
            dataset["h"][i, t] * Y[i, t, s] for i, t, s in u_prime.keys())  # h f olacak unit cost trans
        trans_setup_cost = mdl.sum(
            ((dataset["C"][t]) / 5) * z[i, t, s] for i, t, s in u_prime.keys())  # C F olacak  fixed cost trans
        set_cost = mdl.sum(5 * y[i, t] for i, t in dataset["c"].keys())
        mdl.parameters.timelimit = 50
        mdl.set_time_limit(50)
        profit = revenue - var_cost - trans_cost - trans_setup_cost - set_cost
        mdl.maximize(profit)
        mdl.solve(log_output=True)
        columns = {}
        columns["I"] = mdl.solution.get_value_dict(I)
        columns["I_prime"] = mdl.solution.get_value_dict(I_prime)
        columns["Y"] = mdl.solution.get_value_dict(Y)
        columns["y"] = mdl.solution.get_value_dict(y)
        columns["z"] = mdl.solution.get_value_dict(z)
        columns["x"] = mdl.solution.get_value_dict(x)
        columns["D"] = mdl.solution.get_value_dict(D)
        columns["U"] = mdl.solution.get_value_dict(U)
        columns["v"] = mdl.solution.get_value_dict(v)
        columns["objective_value"] = profit.solution_value
        columns["upper_bound"] = mdl.solve_details.best_bound
        columns["gap"] = mdl.solve_details.mip_relative_gap
    except:
        columns = {}
        columns["objective_value"] = -1e16

    return columns


# samples = pickle.load(open(f"samplesixtytenten.pkl", "rb"))
"""
samples = pickle.load(open(f"samplesixtyfivefive.pkl", "rb"))
T,J,N,i =60,5,5,4
key = (T, J, N, i)
d = samples.get(key)

key=(N,T,J)

res=heuristic_with_transportation(d.get("dataset"),key,0,0)
res1=heuristic_with_transportation(d.get("dataset"),key,list(res["I"].values())[-1],list(res["I_prime"].values())[-1])



print(res['objective_value'])
print(res["gap"])
print(res["upper_bound"])
"""
"""
T,J,N,i =40,5,5,1
key=(N,T,J)
dataset=pickle.load(open(f"datasetDP_{T}_{J}_{N}_{i}.pkl", "rb"))
datasetDP=pickle.load(open(f"dataset_{T}_{J}_{N}_{i}.pkl", "rb"))
d={}
d["dataset"]=datasetDP
d["dataset_DP"]=dataset
res1=heuristic_with_U_cuts(d.get("dataset"),d.get("dataset_DP"),key)
print(res1['objective_value'])
"""
"""
samples = pickle.load(open(f"samplesixtytenten.pkl", "rb"))
for item in samples.keys():
    T,J,N,i = item[0], item[1], item[2], item[3]
    key1 = (T,J,N,i)
    d = samples.get(key1)
    key=(N,T,J)

    res=heuristic_with_transportation(d.get("dataset"),key)
    print(key1)
    print(res['objective_value'])
    print(res["gap"])
    print(res["upper_bound"])
"""
