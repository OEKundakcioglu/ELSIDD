import numpy as np
import pandas as pd


class DatasetGenerator(object):
    def __init__(self, T=40, J=5, N=10,
                 parameters=None):
        if parameters is None:
            parameters = {"S": {"lb": 250, "ub": 300}, "c": {"lb": 0, "ub": 1}, "h": {"lb": 0, "ub": 1},
                          "p": {"lb": 0, "ub": 3}, "C": {"lb": 400, "ub": 1000}, "B": {"lb": 50000, "ub": 75000},
                          "a": {"lb1": 0.6, "ub1": 0.9, "lb2": 0.03, "ub2": 0.04},
                          "u": {"lb1": 1, "ub1": 10, "lb2": 10, "ub2": 20}}
        self.T = T
        self.J = J
        self.N = N
        self.parameters = parameters
        self.data = None
        self.data_dict_CPLEX = None
        self.data_dict_DP = None
        self.seed = None

    def generate(self):

        # generate(a)
        a_df = pd.DataFrame()
        for i in range(self.N):
            a = np.zeros([self.T, self.J + 1])
            a[:, 1] = np.random.uniform(self.parameters["a"]["lb1"], self.parameters["a"]["ub1"], self.T)
            for j in range(2, self.J):
                a[:, j] = a[:, j - 1] - np.random.uniform(self.parameters["a"]["lb2"], self.parameters["a"]["ub2"],
                                                          self.T)
            temp_df = pd.DataFrame(a).reset_index().melt('index')
            temp_df.columns = ['t', 'j', 'value']
            temp_df.insert(loc=0, column='i', value=i + 1)
            temp_df.t += 1
            a_df = a_df.append(temp_df, ignore_index=True)
        # a_df = a_df.round(2)

        # generation of u
        u_df = pd.DataFrame()
        for i in range(self.N):
            u = np.zeros([self.T, self.J + 1])

            u[:, 0] = np.random.uniform(self.parameters["u"]["lb1"], self.parameters["u"]["ub1"], self.T)
            for j in range(1, self.J):
                u[:, j] = u[:, j - 1] + np.random.uniform(self.parameters["u"]["lb2"], self.parameters["u"]["ub2"],
                                                          self.T)
            u[:, self.J] = 25000

            temp_df = pd.DataFrame(u).reset_index().melt('index')
            temp_df.columns = ['t', 'j', 'value']
            temp_df.insert(loc=0, column='i', value=i + 1)
            temp_df.t += 1
            u_df = u_df.append(temp_df, ignore_index=True)

        # u_df = u_df.round(2)

        # generation of S
        S_df = pd.DataFrame()
        for i in range(self.N):
            S = np.random.uniform(self.parameters["S"]["lb"], self.parameters["S"]["ub"], self.T).astype(int)
            temp_df = pd.DataFrame(S).reset_index()
            temp_df.columns = ['t', 'value']
            temp_df.insert(loc=0, column='i', value=i + 1)
            temp_df.t += 1
            S_df = S_df.append(temp_df, ignore_index=True)

        # generation of c
        c_df = pd.DataFrame()
        for i in range(self.N):
            c = np.random.uniform(self.parameters["c"]["lb"], self.parameters["c"]["ub"], self.T)
            temp_df = pd.DataFrame(c).reset_index()
            temp_df.columns = ['t', 'value']
            temp_df.insert(loc=0, column='i', value=i + 1)
            temp_df.t += 1
            c_df = c_df.append(temp_df, ignore_index=True)

        # generation of h
        h_df = pd.DataFrame()
        for i in range(self.N):
            h = np.random.uniform(self.parameters["h"]["lb"], self.parameters["h"]["ub"], self.T + 1)
            h[0] = 0
            temp_df = pd.DataFrame(h).reset_index()
            temp_df.columns = ['t', 'value']
            temp_df.insert(loc=0, column='i', value=i + 1)
            h_df = h_df.append(temp_df, ignore_index=True)
        # h_df = h_df.round(3)

        # generation of p
        p_df = pd.DataFrame()
        for i in range(self.N):
            p = np.random.uniform(self.parameters["p"]["lb"], self.parameters["p"]["ub"], self.T)
            temp_df = pd.DataFrame(p).reset_index()
            temp_df.columns = ['t', 'value']
            temp_df.insert(loc=0, column='i', value=i + 1)
            temp_df.t += 1
            p_df = p_df.append(temp_df, ignore_index=True)
        # p_df = p_df.round(3)

        # generation of C
        C_df = pd.DataFrame()
        C = np.random.uniform(self.parameters["C"]["lb"], self.parameters["C"]["ub"], self.T).astype(int)
        C_df = pd.DataFrame(C).reset_index()
        C_df.columns = ['t', 'value']
        C_df.t += 1

        # generation of B
        B_df = pd.DataFrame()
        B = np.random.uniform(self.parameters["B"]["lb"], self.parameters["B"]["ub"], self.T).astype(int)
        B_df = pd.DataFrame(B).reset_index()
        B_df.columns = ['t', 'value']
        B_df.t += 1

        self.data = {"a": a_df, "u": u_df, "S": S_df, "c": c_df, "h": h_df, "p": p_df, "C": C_df, "B": B_df}

    def getData(self):
        if self.data_dict_CPLEX != None:
            return self.data_dict_CPLEX, self.data_dict_DP
        elif self.data == None:
            print("Dataset is not generated.")
        else:
            # parameters
            a = self.data["a"].set_index(["i", "t", "j"]).to_dict()["value"]

            u = self.data["u"].set_index(["i", "t", "j"]).to_dict()["value"]
            u_prime = self.data["u"][self.data["u"].j != 0].set_index(["i", "t", "j"]).to_dict()["value"]

            S = self.data["S"].set_index(["i", "t"]).to_dict()["value"]
            c = self.data["c"].set_index(["i", "t"]).to_dict()["value"]
            h = self.data["h"].set_index(["i", "t"]).to_dict()["value"]
            p = self.data["p"].set_index(["i", "t"]).to_dict()["value"]
            C = self.data["C"].set_index(["t"]).to_dict()["value"]
            B = self.data["B"].set_index(["t"]).to_dict()["value"]

            d = {}

            for i in range(1, self.N + 1):
                for t in range(1, self.T + 1):
                    d[i, t, 0] = round((1.0 - a[i, t, 1]) * u[i, t, 0], 3)
                    # u[i, t, 0] = 0
                    # d[i, t, 0] = d[i, t, 0] + a[i, t, 1] * u[i, t, 0], 3
                    for j in range(1, self.J + 1):
                        d[i, t, j] = d[i, t, j - 1] + a[i, t, j] * (u[i, t, j] - u[i, t, j - 1])

            self.data_dict_CPLEX = {"a": a, "d": d, "u": u, "S": S, "c": c, "h": h, "p": p, "C": C, "B": B}

            temp_data_DP = {}

            for p_id in range(1, self.N + 1):
                temp_data_DP[p_id] = self.generateDP(p_id)

            self.data_dict_DP = temp_data_DP

            return self.data_dict_CPLEX, self.data_dict_DP

    def generateDP(self, p_id):
        temp_data = self.data_dict_CPLEX

        a = np.zeros(shape=(self.T + 1, self.J + 1))  # segment slopes
        u = np.zeros(shape=(self.T + 1, self.J + 1))  # segment bounds
        d = np.zeros(shape=(self.T + 1, self.J + 1))  # function values at segment bounds
        i = np.zeros(shape=(self.T + 1, self.J + 1))
        I = np.zeros(shape=(self.T + 1, self.T + 1, self.J + 1))
        U = np.zeros(shape=(self.T + 1, self.T + 1, self.J + 1))
        D = np.zeros(shape=(self.T + 1, self.T + 1, self.J + 1))
        S = np.zeros(shape=(self.T + 1))
        p = np.zeros(shape=(self.T + 1))
        c = np.zeros(shape=(self.T + 1))
        h = np.zeros(shape=(self.T + 1))

        for t in range(1, self.T + 1):
            S[t] = temp_data["S"][p_id, t]
            c[t] = temp_data["c"][p_id, t]
            h[t] = temp_data["h"][p_id, t]
            p[t] = temp_data["p"][p_id, t]
            for j in range(0, self.J + 1):
                u[t, j] = temp_data["u"][p_id, t, j]
                d[t, j] = temp_data["d"][p_id, t, j]
                a[t, j] = temp_data["a"][p_id, t, j]

        for t in range(1, self.T + 1):
            for j in range(0, self.J + 1):
                i[t, j] = u[t, j] - d[t, j]

        U, I, D = ComputeUIrtj(U, I, D, u, a, d, i, self.T, self.J)

        return {"a": a, "d": d, "u": u, "S": S, "c": c, "h": h, "p": p, "i": i, "I": I, "U": U, "D": D}


def determineUgivenI(I_, r, i, u, a, J):
    U = -1000
    for j in range(1, J + 1):
        if I_ >= i[r, j - 1]:
            U = np.copy(u[r, j - 1] + (I_ - i[r, j - 1]) / (1 - a[r, j]))
    return U


def g(t, U_, u, a, d, J):
    demand = -1000
    if U_ < 0:
        demand = 0
    elif U_ < u[t, 0]:
        demand = np.copy(d[t, 0] - a[t, 1] * (U_ - u[t, 0]))
    else:
        for j in range(1, J + 1):
            if U_ >= u[t, j - 1]:
                demand = np.copy(d[t, j - 1] + a[t, j] * (U_ - u[t, j - 1]))
    return demand


def ComputeUIrtj(U, I, D, u, a, d, i, T, J):
    for t in range(0, T + 1):
        for j in range(0, J + 1):
            U[t, t, j] = np.copy(u[t, j])
            for r in range(t, T + 1):
                D[r, t, j] = np.copy(g(r, U[r, t, j], u, a, d, J))
                I[r, t, j] = np.copy(U[r, t, j] - D[r, t, j])
                if r <= T - 1:
                    U[r + 1, t, j] = np.copy(I[r, t, j])
    for t in range(T, 0, -1):
        for j in range(0, J + 1):
            for r in range(t - 1, -1, -1):
                I[r, t, j] = np.copy(U[r + 1, t, j])
                U[r, t, j] = np.copy(determineUgivenI(I[r, t, j], r, i, u, a, J))
                D[r, t, j] = np.copy(g(r, U[r, t, j], u, a, d, J))
    return U, I, D


"""
data_params = {
    "S": {"lb": 100, "ub": 300},
    "c": {"lb": 0, "ub": 1},
    "h": {"lb": 0, "ub": 1},
    "p": {"lb": 2, "ub": 3},
    "C": {"lb": 1000, "ub": 3500}, #600 100 arası
    "B": {"lb": 1000, "ub": 12000},
    "a": {"lb1": 0.7, "ub1": 0.9, "lb2": 0.03, "ub2": 0.04},
    "u": {"lb1": 10, "ub1": 20, "lb2": 0, "ub2": 20}
}

T_list = [60]
J_list = [10]
N_list = [20]

os.makedirs('dataset', exist_ok=True)

list_of_datasets={}
for T in T_list:
    for J in J_list:
        for N in N_list:
            for i in range(1,10):
                key = (T, J, N, i)
                dataModel = DatasetGenerator(T, J, N, parameters=data_params)
                dataModel.generate()
                dataset, datasetDP = dataModel.getData()
                list_of_datasets[key]={}
                list_of_datasets[key]["dataset"]=dataset
                list_of_datasets[key]["dataset_DP"]= datasetDP
                
                
                file_name = "dataset_{}_{}_{}_{}".format(T, J, N, i)
                f = open(file_name + '.pkl', "wb")
                pickle.dump(dataset, f)
                f.close()

                file_name = "datasetDP_{}_{}_{}_{}".format(T, J, N, i)
                f = open(file_name + '.pkl', "wb")
                pickle.dump(datasetDP, f)
                f.close()
                
                
file_name="sixtytentwenty"
f=open(file_name + '.pkl', "wb")  
pickle.dump(list_of_datasets, f)             
f.close()
"""
