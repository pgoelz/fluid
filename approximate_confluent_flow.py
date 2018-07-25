from math import inf

from gurobipy.gurobipy import GRB, Model, quicksum

from configure_gurobi import configure_gurobi
from fractional_integral_flow import SplittableFlow
from simulations import EPS, ConfluentMechanism


class OnePlusLogTwoApproximation(ConfluentMechanism):
    PLOT_COLOR = "brown"
    PLOT_ABBREVIATION = "A"
    PLOT_LABEL = "($1 + \\log_2 |V|$)-approximation"
    PLOT_PATTERN = "solid"

    @staticmethod
    def _contract(flow_graph, node, into_node, demands):
        assert node != into_node

        for succs in flow_graph:
            for neighbor in succs:
                if neighbor == node:
                    if into_node in succs:
                        succs[into_node] += succs[neighbor]
                    else:
                        succs[into_node] = succs[neighbor]
                    del succs[neighbor]

        # TODO: Check that this is valid
        flow_graph[node] = {}
        demands[into_node] += demands[node]
        demands[node] = 0

    def _decrease_flow_or_inv_flow(self, flow_graph, f_min, node_from, node_to):
        if self.graph.is_voter(node_from):
            sign = -1
            node_from, node_to = node_to, node_from
        else:
            sign = 1
        assert not self.graph.is_voter(node_from)
        assert node_to in flow_graph[node_from]

        flow_graph[node_from][node_to] -= sign * f_min
        assert flow_graph[node_from][node_to] >= -EPS
        if flow_graph[node_from][node_to] <= EPS:
            del flow_graph[node_from][node_to]

    def _create_g_hat(self, flow_graph):
        graph = [[] for _ in range(len(flow_graph))]
        for i, succs in enumerate(flow_graph):
            for neighbor in succs:
                graph[i].append(neighbor)
                if self.graph.is_voter(neighbor):
                    graph[neighbor].append(i)
        return graph

    @staticmethod
    def detect_cycles_longer_than_two(graph):
        """

        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[1],[2],[0]])
        [0, 1, 2, 0]
        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[1], [0], [0]])

        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[4], [2], [3], [1], [0]])
        [1, 2, 3, 1]
        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[]])

        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[1], [2], [3], [2]])

        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[1], [2], [3], [4], [1]])
        [1, 2, 3, 4, 1]
        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[], [0, 0, 2], [0, 3], [1, 0]])
        [1, 2, 3, 1]
        >>> OnePlusLogTwoApproximation.detect_cycles_longer_than_two([[], [2], [3], [0]])


        Args:
            graph (list of list of int): in adjacency list representation
        Returns:
            list of ints: node indices of a loop, first element is successor of the last.
        """
        entered = set()
        left = set()

        def dfs(node, predecessor):
            if node in entered:
                return None
            entered.add(node)

            for neighbor in graph[node]:
                assert neighbor != node
                if neighbor == predecessor or neighbor in left:
                    continue
                if neighbor in entered:
                    return [node, neighbor]
                else:
                    result = dfs(neighbor, node)
                    if result is not None:
                        return [node] + result

            left.add(node)
            return None

        for i in range(len(graph)):
            result = dfs(i, None)
            if result is not None:
                assert len(result) > 3
                assert result[0] == i
                loop_point = result[-1]
                assert result[-2] != loop_point  # cycle of length 1
                assert result[-3] != loop_point  # cycle of length 2
                assert result.count(loop_point) >= 2

                for j in range(4, len(result) + 1):
                    if result[-j] == loop_point:
                        return result[-j:]
                assert False

        return None

    def _node_aggregation(self, flow_graph, transitive_delegations, demands):
        for i, succs in enumerate(flow_graph):
            if len(succs) == 1:
                delegate = list(succs.keys())[0]
                if self.graph.is_voter(delegate):
                    transitive_delegations[i] = delegate
                    self._contract(flow_graph, i, delegate, demands)
                    return True
        return False

    def _breaking_sawtooth_cycles(self, flow_graph):
        g_hat = self._create_g_hat(flow_graph)

        cycle = self.detect_cycles_longer_than_two(g_hat)
        assert cycle is None or len(cycle) >= 4  # minimal circle length 3 + repeated point 1
        if cycle is not None:
            f_min = inf
            for i in range(len(cycle) - 1):
                if cycle[i + 1] in flow_graph[cycle[i]]:
                    f_min = min(f_min, flow_graph[cycle[i]][cycle[i + 1]])
            assert f_min < inf

            for i in range(len(cycle) - 1):
                self._decrease_flow_or_inv_flow(flow_graph, f_min, cycle[i], cycle[i + 1])

            return True
        return False

    def _sink_deactivation(self, flow_graph, demands):
        num_agents = len(flow_graph)

        predecessors = [[] for _ in range(num_agents)]
        inflow = [0. for _ in range(num_agents)]
        number_of_sink_successors = [0 for _ in range(num_agents)]
        for i, succs in enumerate(flow_graph):
            for neighbor in succs:
                assert succs[neighbor] >= EPS
                predecessors[neighbor].append(i)
                inflow[neighbor] += succs[neighbor]
                if self.graph.is_voter(neighbor):
                    number_of_sink_successors[i] += 1

        sj = None
        for i in range(num_agents):
            if (self.graph.is_voter(i) and len(predecessors[i]) == 1
                and number_of_sink_successors[predecessors[i][0]] >= 2):
                sj = i
                break
        assert sj is not None
        v = predecessors[sj][0]
        sl = None
        for neighbor in flow_graph[v]:
            if neighbor != sj and self.graph.is_voter(neighbor):
                sl = neighbor
                break
        assert sl is not None
        if demands[sj] + inflow[sj] + flow_graph[v][sl] < demands[sl] + inflow[sl] - flow_graph[v][sl]:
            flow_graph[v][sj] += flow_graph[v][sl]
            del flow_graph[v][sl]
        else:
            flow_graph[v][sl] += flow_graph[v][sj]
            del flow_graph[v][sj]

    def _transitive_delegations_to_delegations(self, transitive_delegations):
        delegations_dict = {}

        num_agents = len(transitive_delegations)
        predecessors = [[] for _ in range(num_agents)]
        for i in range(num_agents):
            if self.graph.is_voter(i):
                delegations_dict[i] = None
            else:
                for neighbor in self.graph.potential_delegations[i]:
                    predecessors[neighbor].append(i)

        def dfs(node):
            assert node in delegations_dict
            for pred in predecessors[node]:
                if pred in delegations_dict:
                    continue
                if transitive_delegations[pred] != transitive_delegations[node]:
                    continue
                delegations_dict[pred] = node
                dfs(pred)

        for i in range(num_agents):
            if self.graph.is_voter(i):
                dfs(i)

        assert len(delegations_dict) == num_agents
        return [delegations_dict[i] for i in range(num_agents)]

    def get_delegations(self, time_out=None):
        num_agents = self.graph.number_of_nodes()
        transitive_delegations = [i for i in range(num_agents)]
        demands = [1 for _ in range(num_agents)]

        flow_graph = SplittableFlow.solve_flow(self.graph.potential_delegations)[0]

        assert len(flow_graph) == num_agents
        for i, succs in enumerate(flow_graph):
            if succs is None:
                assert self.graph.is_voter(i)
            else:
                assert len(succs) > 0
                assert all(succs[neighbor] >= EPS for neighbor in succs)
                assert all(neighbor != i for neighbor in succs)

        new_flow = []
        for succs in flow_graph:
            if succs is None:
                new_flow.append({})
            else:
                new_flow.append(succs)

        while any(len(succs) > 0 for succs in new_flow):
            if self._node_aggregation(new_flow, transitive_delegations, demands):
                continue
            if self._breaking_sawtooth_cycles(new_flow):
                continue
            self._sink_deactivation(new_flow, demands)

        delegations = self._transitive_delegations_to_delegations(transitive_delegations)

        return delegations


class OnePlusLnApproximation(OnePlusLogTwoApproximation):
    PLOT_COLOR = "#4CAF50"
    PLOT_ABBREVIATION = "a"
    PLOT_LABEL = "($1 + \\log |V|$)-approximation"
    PLOT_PATTERN = "solid"

    @staticmethod
    def sink_strongly_connected_component(graph):
        """Compute a strongly connected component (SCC) that is a sink in the DAG of SCCs.

        Isolated sinks are not reported. The function assumes that all sinks are isolated.

        >>> OnePlusLnApproximation.sink_strongly_connected_component([[1], [2], [0]])
        [0, 1, 2]
        >>> OnePlusLnApproximation.sink_strongly_connected_component([[1], [2], [1]])
        [1, 2]
        >>> OnePlusLnApproximation.sink_strongly_connected_component([[], [2], [1]])
        [1, 2]

        Args:
            graph (list of list of int): graph in adjacency list representation
        Returns:
            list of int:
            list of all nodes in the
        """

        num_nodes = len(graph)
        dfs_num = [None for _ in range(num_nodes)]  # Iteration counter when visited for the first time
        dfs_low = [0 for _ in range(num_nodes)]  # Lowest dfs_num reachable from DFS spanning subtree of node
        visited = [False for _ in range(num_nodes)]
        dfs_number_counter = 0
        stack = []

        def tarjan_scc(u):
            nonlocal dfs_number_counter, dfs_num, dfs_low, visited, stack

            assert not visited[u]

            dfs_low[u] = dfs_number_counter
            dfs_num[u] = dfs_number_counter
            dfs_number_counter += 1

            stack.append(u)
            visited[u] = True

            for neighbor in graph[u]:
                if dfs_num[neighbor] is None:
                    inner = tarjan_scc(neighbor)
                    if inner is not None:
                        return inner
                assert visited[neighbor]
                if visited[neighbor]:
                    dfs_low[u] = min(dfs_low[u], dfs_low[neighbor])

            if dfs_low[u] == dfs_num[u]:
                index = stack.index(u)
                assert index == dfs_num[u]
                return stack[index:]

            return None

        for i in range(num_nodes):
            if len(graph[i]) > 0 and dfs_num[i] is None:
                inner = tarjan_scc(i)
                if inner is not None:
                    return inner
        assert False

    def _balancing(self, flow_graph, sinks, frontier, demands):
        configure_gurobi()
        model = Model()

        xij = {i: {} for i in frontier}
        for node in frontier:
            congestion = sum(flow_graph[node][neighbor] for neighbor in flow_graph[node])
            for neighbor in flow_graph[node]:
                assert neighbor in sinks
                xij[node][neighbor] = model.addVar(vtype=GRB.CONTINUOUS, name=f"x_{node}_{neighbor}")
                model.addConstr(xij[node][neighbor] >= 0)
            model.addConstr(quicksum(xij[node][neighbor] for neighbor in flow_graph[node]) == congestion)

        sink_predecessors = {i: [] for i in sinks}
        for node in frontier:
            for neighbor in flow_graph[node]:
                sink_predecessors[neighbor].append(node)

        bj = {}
        for node in sinks:
            bj[node] = model.addVar(vtype=GRB.CONTINUOUS, name=f"b_{node}")
            model.addConstr(bj[node] == quicksum(xij[pred][node] for pred in sink_predecessors[node]) + demands[node])

        model.setObjective(quicksum(bj[node] * bj[node] for node in sinks), GRB.MINIMIZE)
        model.optimize()

        any_edge_deleted = False
        for node in frontier:
            to_delete = []
            for neighbor in flow_graph[node]:
                flow = xij[node][neighbor].X
                if flow < EPS:
                    to_delete.append(neighbor)
                    any_edge_deleted = True
                else:
                    flow_graph[node][neighbor] = flow
            for neighbor in to_delete:
                del flow_graph[node][neighbor]

        return any_edge_deleted

    def _improved_sink_deactivation(self, flow_graph, demands):
        g_hat = self._create_g_hat(flow_graph)
        scc = self.sink_strongly_connected_component(g_hat)
        assert len(scc) >= 3

        sinks = []
        frontier = []
        for node in scc:
            if self.graph.is_voter(node):
                sinks.append(node)
            else:
                frontier.append(node)
        assert len(sinks) > 0

        if self._balancing(flow_graph, sinks, frontier, demands):
            return

        sinks_predecessors = {i: [] for i in sinks}
        sinks_inflow = {i: 0. for i in sinks}
        for node in frontier:
            for neighbor in flow_graph[node]:
                sinks_predecessors[neighbor].append(node)
                sinks_inflow[neighbor] += flow_graph[node][neighbor]

        min_inflow_sink = sinks[0]
        for node in sinks[1:]:
            if sinks_inflow[node] < sinks_inflow[min_inflow_sink]:
                min_inflow_sink = node

        for pred in sinks_predecessors[min_inflow_sink]:
            assert len(flow_graph[pred]) >= 2
            neighbors = list(flow_graph[pred].keys())
            if min_inflow_sink == neighbors[0]:
                alternative_sink = neighbors[1]
                assert alternative_sink != min_inflow_sink
            else:
                alternative_sink = neighbors[0]

            flow_graph[pred][alternative_sink] += flow_graph[pred][min_inflow_sink]
            del flow_graph[pred][min_inflow_sink]

        sinks.remove(min_inflow_sink)

        self._balancing(flow_graph, sinks, frontier, demands)

    def get_delegations(self, time_out=None):
        num_agents = self.graph.number_of_nodes()
        transitive_delegations = [i for i in range(num_agents)]
        demands = [1 for _ in range(num_agents)]

        # list of (dict of int → float): for each node, dictionary mapping successors to positive flow
        flow_graph = SplittableFlow.solve_flow(self.graph.potential_delegations)[0]

        assert len(flow_graph) == num_agents
        for i, succs in enumerate(flow_graph):
            if succs is None:
                assert self.graph.is_voter(i)
            else:
                assert len(succs) > 0
                assert all(succs[neighbor] >= EPS for neighbor in succs)
                assert all(neighbor != i for neighbor in succs)

        new_flow = []
        for succs in flow_graph:
            if succs is None:
                new_flow.append({})
            else:
                new_flow.append(succs)

        while any(len(succs) > 0 for succs in new_flow):
            if self._node_aggregation(new_flow, transitive_delegations, demands):
                continue
            if self._breaking_sawtooth_cycles(new_flow):
                continue
            self._improved_sink_deactivation(new_flow, demands)

        delegations = self._transitive_delegations_to_delegations(transitive_delegations)

        return delegations


if __name__ == "__main__":
    from doctest import testmod
    testmod()
