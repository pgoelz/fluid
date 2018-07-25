from os import getenv
from gurobipy import setParam


def configure_gurobi():
    setParam("OutputFlag", False)
    if getenv("GUROBI_SINGLE_THREAD") is not None:
        setParam("Threads", 1)
