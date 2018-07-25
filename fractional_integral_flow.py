from gurobipy import GRB, Model, quicksum

from configure_gurobi import configure_gurobi
from simulations import EPS, SplittableMechanism, ConfluentMechanism


class SplittableFlow(SplittableMechanism):
    PLOT_COLOR = "#9C27B0"
    PLOT_ABBREVIATION = "s"
    PLOT_LABEL = "optimal splittable flow"
    PLOT_PATTERN = "solid"

    @staticmethod
    def solve_flow(potential_delegations):
        """Minimize congestion for splittable flow by solving a linear program.
        Assumes that a sink is reachable from every node.

        Args:
            potential_delegations (list of (list of int / None)): adjacency list representation of the graph

        Returns:
            (list of ((dict of int → float) / None), float): (splittable flow, maximum congestion)

        >>> SplittableFlow.solve_flow([None, [0], [1, 1], None])
        ([None, {0: 2.0}, {1: 1.0}, None], 3.0)
        >>> SplittableFlow.solve_flow([None, None, [0, 1], [1]])
        ([None, None, {0: 1.0}, {1: 1.0}], 2.0)
        >>> SplittableFlow.solve_flow([None, None, [0, 1]]) == ([None, None, {0: 0.5, 1: 0.5}], 1.5)
        True

        Linear program variables:
            z = minimization objective, equal to maximum weight of any sink
            f(u, v) = flow through edge (u, v)

        minimize z

        subject to
            Σ f(_, v) + 1 <= z        ∀ sinks v
            1 + Σ f(_, u) = Σ f(u, _) ∀ non-sinks u
            f(u, v) >= 0              ∀ adjacent u, v
        (The sums range over the implicit argument denoted by an underscore.)
        """

        unique_edges = []
        for delegations in potential_delegations:
            if delegations is None:
                unique_edges.append(None)
            else:
                unique_edges.append(list(set(delegations)))

        configure_gurobi()
        model = Model("splittable_flow")
        z = model.addVar(vtype=GRB.CONTINUOUS, name="z")

        predecessors = {i: set() for i in range(len(unique_edges))}
        flow = {}
        for u, edges in enumerate(unique_edges):
            if edges is not None:
                for v in edges:
                    flow[(u, v)] = model.addVar(vtype=GRB.CONTINUOUS, name=f"flow_{u}_{v}")
                    model.addConstr(flow[(u, v)] >= 0)
                    predecessors[v].add(u)

        for u, edges in enumerate(unique_edges):
            if edges is not None:
                model.addConstr(
                    quicksum(flow[(u, v)] for v in edges) == quicksum(flow[(v, u)] for v in predecessors[u]) + 1)
            else:
                model.addConstr(z >= quicksum(flow[(v, u)] for v in predecessors[u]) + 1)

        model.setObjective(z, GRB.MINIMIZE)
        model.optimize()

        flow_list = []
        for u, edges in enumerate(unique_edges):
            if edges is None:
                flow_list.append(None)
            else:
                out_flow = {}
                assert sum(flow[(u, v)].X for v in edges) >= 1 - EPS
                for v in edges:
                    if flow[(u, v)].X > EPS:
                        out_flow[v] = flow[(u, v)].X
                flow_list.append(out_flow)
        return flow_list, z.X

    def get_delegations(self, time_out=None):
        return self.solve_flow(self.graph.potential_delegations)[0]


class ConfluentFlow(ConfluentMechanism):
    PLOT_COLOR = "#3F51B5"
    PLOT_ABBREVIATION = "c"
    PLOT_LABEL = "optimal confluent flow"
    PLOT_PATTERN = "solid"

    @staticmethod
    def is_splittable():
        return False

    @staticmethod
    def solve_flow(potential_delegations, time_out=None):
        """Minimize congestion for confluent flow by solving a Mixed Integer Linear Program.
        Assumes that a sink is reachable from every node.

        Args:
            potential_delegations (list of (list of int / None)): adjacency list representation of the graph
            time_out (float / None): Timeout in seconds, None for unbounded running time

        Returns:
            (list of (int / None), float): (optimal flow, maximum congestion)

        >>> ConfluentFlow.solve_flow([None, [0], [1, 1], None])
        ([None, 0, 1, None], 3)
        >>> ConfluentFlow.solve_flow([None, None, [0, 1], [1]])
        ([None, None, 0, 1], 2)
        >>> ConfluentFlow.solve_flow([None, None, [0, 1]])[1]
        2
        
        MILP variables:
            z = minimization objective, equal to maximum weight of any sink
            f(u, v) = flow through edge (u, v)
            x(u, v) = binary indicator variable for edges; if zero, flow must be zero
            
        M is a large enough constant, here set as the number of nodes

        minimize z

        subject to
            Σ f(_, v) + 1 <= z        ∀ sinks v
            1 + Σ f(_, u) = Σ f(u, _) ∀ non-sinks u
            f(u, v) >= 0              ∀ adjacent u, v
            f(u, v) <= M * x(u, v)    ∀ adjacent u, v
            Σ x(u, _) = 1             ∀ non-sinks u
        (The sums range over the implicit argument denoted by an underscore.)
        """

        unique_edges = []
        for delegations in potential_delegations:
            if delegations is None:
                unique_edges.append(None)
            else:
                unique_edges.append(list(set(delegations)))

        configure_gurobi()
        model = Model("confluent_flow")
        z = model.addVar(vtype=GRB.INTEGER, name="z")
        M = len(unique_edges)

        predecessors = {i: set() for i in range(len(unique_edges))}
        flow = {}
        x = {}
        for u, edges in enumerate(unique_edges):
            if edges is not None:
                for v in edges:
                    flow[(u, v)] = model.addVar(vtype=GRB.INTEGER, name=f"flow_{u}_{v}")
                    model.addConstr(flow[(u, v)] >= 0)
                    x[(u, v)] = model.addVar(vtype=GRB.BINARY, name=f"x_{u}_{v}")
                    predecessors[v].add(u)
                    model.addConstr(flow[(u, v)] <= M * x[(u, v)])
                model.addConstr(quicksum(x[(u, v)] for v in edges) == 1)

        for u, edges in enumerate(unique_edges):
            if edges is not None:
                model.addConstr(
                    quicksum(flow[(u, v)] for v in edges) == quicksum(flow[(v, u)] for v in predecessors[u]) + 1)
            else:
                model.addConstr(z >= quicksum(flow[(v, u)] for v in predecessors[u]) + 1)

        model.setObjective(z, GRB.MINIMIZE)
        if time_out is not None:
            model.setParam('TimeLimit', time_out)
        model.optimize()

        delegations = [None for _ in unique_edges]
        for u, edges in enumerate(unique_edges):
            if edges is not None:
                for v in edges:
                    if flow[(u, v)].X > EPS:
                        assert delegations[u] is None
                        delegations[u] = v

        return delegations, round(z.X)

    def get_delegations(self, time_out=None):
        return self.solve_flow(self.graph.potential_delegations, time_out)[0]


if __name__ == "__main__":
    from doctest import testmod
    testmod()
