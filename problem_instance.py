import pickle
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=False)
class ProblemInstance:
    name: str
    T: int
    J: int
    N: int
    a: np.ndarray  # shape: N, T+1, J+1
    u: np.ndarray  # shape: N, T+1, J+1
    d: np.ndarray  # shape: N, T+1, J+1
    i: np.ndarray  # shape: N, T+1, J+1
    I: np.ndarray  # shape: N, T+1, T+1, J+1
    U: np.ndarray  # shape: N, T+1, T+1, J+1
    D: np.ndarray  # shape: N, T+1, T+1, J+1
    S: np.ndarray  # shape: N, T+1
    p: np.ndarray  # shape: N, T+1
    c: np.ndarray  # shape: N, T+1
    h: np.ndarray  # shape: N, T+1
    C: np.ndarray
    

        

class DatasetGenerator:
    def __init__(self, T, J, N, parameters=None):
        if parameters is None:
            self.parameters = {"S": {"lb": 250, "ub": 300}, "c": {"lb": 0, "ub": 1}, "h": {"lb": 0, "ub": 1},
                               "p": {"lb": 0, "ub": 3}, "C": {"k": 1,"f":10},
                               "a": {"lb1": 0.6, "ub1": 0.9, "lb2": 0.03, "ub2": 0.04},
                               "u": {"lb1": 1, "ub1": 10, "lb2": 10, "ub2": 20}}
        else:
            self.parameters = parameters

        self.T = T
        self.J = J
        self.N = N
        self.generate()

    def generate(self):

        # generate(a)
        a = np.zeros([self.N, self.T+1, self.J + 1])
        for n in range(self.N):
            temp_a = np.zeros([self.T+1, self.J + 1])
            temp_a[:, 1] = np.random.uniform(
                self.parameters["a"]["lb1"], self.parameters["a"]["ub1"], self.T+1)
            for j in range(2, self.J):
                temp_a[:, j] = temp_a[:, j - 1] - np.random.uniform(
                    self.parameters["a"]["lb2"], self.parameters["a"]["ub2"], self.T+1)
            temp_a[0] = np.zeros(self.J + 1)
            a[n] = np.round(temp_a, 3)

        # generation of u
        u = np.zeros([self.N, self.T+1, self.J + 1])
        for n in range(self.N):
            temp_u = np.zeros([self.T+1, self.J + 1])

            temp_u[:, 0] = np.random.uniform(
                self.parameters["u"]["lb1"], self.parameters["u"]["ub1"], self.T+1)
            for j in range(1, self.J):
                temp_u[:, j] = temp_u[:, j - 1] + np.random.uniform(
                    self.parameters["u"]["lb2"], self.parameters["u"]["ub2"], self.T+1)
            temp_u[:, self.J] = 250000
            temp_u[0] = np.zeros(self.J + 1)
            u[n] = temp_u.astype(int)

        # generation of S
        S = np.zeros([self.N, self.T+1])
        for n in range(self.N):
            S[n] = np.random.uniform(
                self.parameters["S"]["lb"], self.parameters["S"]["ub"], self.T+1).astype(int)
            S[n, 0] = 0

        # generation of c
        c = np.zeros([self.N, self.T+1])
        for n in range(self.N):
            c[n] = np.round(np.random.uniform(
                self.parameters["c"]["lb"], self.parameters["c"]["ub"], self.T+1), 2)
            c[n, 0] = 0

        # generation of h
        h = np.zeros([self.N, self.T+1])
        for n in range(self.N):
            h[n] = np.round(np.random.uniform(
                self.parameters["h"]["lb"], self.parameters["h"]["ub"], self.T+1), 2)
            h[n, 0] = 0

         # generation of p
        p = np.zeros([self.N, self.T+1])
        for n in range(self.N):
            p[n] = np.round(np.random.uniform(
                self.parameters["p"]["lb"], self.parameters["p"]["ub"], self.T+1), 2)
            p[n, 0] = 0

        i = np.zeros([self.N, self.T+1, self.J + 1])
        d = np.zeros([self.N, self.T+1, self.J + 1])
        for n in range(self.N):
            for t in range(1, self.T + 1):
                d[n, t, 0] = int((1-a[n, t, 1])*u[n, t, 0])
                i[n, t, 0] = u[n, t, 0]-d[n, t, 0]
                for j in range(1, self.J + 1):
                    d[n, t, j] = int(d[n, t, j - 1] + a[n, t, j]
                                     * (u[n, t, j] - u[n, t, j - 1]))
                    i[n, t, j] = u[n, t, j]-d[n, t, j]

        U = np.zeros([self.N, self.T+1, self.T+1, self.J + 1])
        D = np.zeros([self.N, self.T+1, self.T+1, self.J + 1])
        I = np.zeros([self.N, self.T+1, self.T+1, self.J + 1])
        for n in range(self.N):
            for t in range(self.T + 1):
                for j in range(self.J + 1):
                    U[n, t, t, j] = u[n, t, j]
                    for r in range(t, self.T + 1):
                        # g function
                        D[n, r, t, j] = -1000
                        if U[n, r, t, j] < 0:
                            D[n, r, t, j] = 0
                        elif U[n, r, t, j] < u[n, r, 0]:
                            D[n, r, t, j] = d[n, r, 0]-a[n, r, 1] * \
                                (U[n, r, t, j]-u[n, r, 0])
                        else:
                            for j_ in range(1, self.J+1):
                                if U[n, r, t, j] >= u[n, r, j_-1]:
                                    D[n, r, t, j] = d[n, r, j_-1] + \
                                        a[n, r, j] * \
                                        (U[n, r, t, j_]-u[n, r, j_-1])

                        I[n, r, t, j] = U[n, r, t, j]-D[n, r, t, j]

                        if r <= self.T-1:
                            U[n, r+1, t, j] = np.copy(I[n, r, t, j])
            for t in range(self.T, 0, -1):
                for j in range(self.J+1):
                    for r in range(t-1, -1, -1):
                        I[n, r, t, j] = np.copy(U[n, r+1, t, j])

                        U[n, r, t, j] = -1000
                        for j_ in range(1, self.J+1):
                            if I[n, r, t, j] >= i[n, r, j-1]:
                                U[n, r, t, j] = np.copy(
                                    u[n, r, j-1]+(I[n, r, t, j]-i[n, r, j-1])/(1-a[n, r, j]))

                        D[n, r, t, j] = -1000
                        if U[n, r, t, j] < 0:
                            D[n, r, t, j] = 0
                        elif U[n, r, t, j] < u[n, r, 0]:
                            D[n, r, t, j] = d[n, r, 0]-a[n, r, 1] * \
                                (U[n, r, t, j]-u[n, r, 0])
                        else:
                            for j_ in range(1, self.J+1):
                                if U[n, r, t, j] >= u[n, r, j_-1]:
                                    D[n, r, t, j] = d[n, r, j_-1] + \
                                        a[n, r, j] * \
                                        (U[n, r, t, j_]-u[n, r, j_-1])
      
        C_val = round(u[:, 1:, 0][:, self.parameters["C"]["k"]:].sum()/(self.T-self.parameters["C"]["k"]))*self.parameters["C"]["f"]

        C = np.full(self.T + 1, C_val)

        #time_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file_name = "dataset_{}_{}_{}".format(
            self.T, self.J, self.N)

        self.data = ProblemInstance(name=self.file_name, N=self.N, T=self.T, J=self.J, a=a, u=u,
                                    S=S, c=c, h=h, p=p, i=i, d=d, I=I, U=U, D=D, C=C)
        
        self.load_data()
        self.export_data()
        #self.data = {"a": a, "u": u, "S": S, "c": c, "h": h, "p": p, "i": i, "d": d, "I": I, "U": U, "D": D, "C": C, "B": B, "pi": pi}

    def load_data(self):
        return self.data
    

    def export_data(self):
            f = open("{}.pkl".format(self.file_name), "wb")
            pickle.dump(self.data, f)
            f.close()
"""
DatasetGenerator()
object1 = pd.read_pickle("dataset_40_5_5.pkl")
aDict = vars(object1)
"""


