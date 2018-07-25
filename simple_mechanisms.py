from math import inf

from numpy.random.mtrand import choice

from simulations import ConfluentMechanism


class NoChoice(ConfluentMechanism):
    PLOT_COLOR = "grey"
    PLOT_ABBREVIATION = "n"
    PLOT_LABEL = "single delegation"
    PLOT_PATTERN = "solid"

    def __init__(self, graph):
        super().__init__(graph)
        if graph.outdegree != 1:
            raise ValueError("NoChoice mechanism can only be applied to graphs with outdegree 1.")
        self.delegations = [None]

    def notify_of_added_voting_node(self):
        self.delegations.append(None)

    def notify_of_added_delegating_node(self, potential_delegations):
        assert len(potential_delegations) == 1
        self.delegations.append(potential_delegations[0])

    def get_delegations(self, time_out=None):
        return self.delegations


class GreedyNewestDelegate(ConfluentMechanism):
    """Online algorithm that always delegates to the most-recently generated node from its potential delegations."""
    PLOT_COLOR = "violet"
    PLOT_ABBREVIATION = "w"
    PLOT_LABEL = "greedy newest delegate"
    PLOT_PATTERN = "solid"

    def __init__(self, graph):
        super().__init__(graph)
        self.delegations = [None]

    def notify_of_added_voting_node(self):
        self.delegations.append(None)

    def notify_of_added_delegating_node(self, potential_delegations):
        super().notify_of_added_delegating_node(potential_delegations)
        self.delegations.append(max(potential_delegations))

    def get_delegations(self, time_out=None):
        return self.delegations


class GreedyPowerOfChoice(ConfluentMechanism):
    """Online algorithm that always delegates to the option that transitively delegates to the voter with least weight.

    Attributes:
        delegations (list of (int / None)): For each node, the id of the node it delegates to; None for voters.
        transitive_delegations (list of int): For each node, the id of the voter it transitively delegates to
        voter_weights (list of int): For a voter, its weight; for all other nodes zero
    """

    PLOT_COLOR = "#FF9800"
    PLOT_ABBREVIATION = "p"
    PLOT_LABEL = "greedy power of choice"
    PLOT_PATTERN = "solid"

    def __init__(self, graph):
        super().__init__(graph)

        self.delegations = [None]
        self.transitive_delegations = [0]
        self.voter_weights = [1]

        self._check_assertions()

    def _check_assertions(self):
        assert len(self.delegations) == self.graph.number_of_nodes()
        assert len(self.transitive_delegations) == self.graph.number_of_nodes()
        assert len(self.voter_weights) == self.graph.number_of_nodes()
        assert sum(self.voter_weights) == self.graph.number_of_nodes()

    def notify_of_added_voting_node(self):
        number = self.graph.number_of_nodes() - 1
        self.delegations.append(None)
        self.transitive_delegations.append(number)
        self.voter_weights.append(1)

        self._check_assertions()

    def notify_of_added_delegating_node(self, potential_delegations):
        super().notify_of_added_delegating_node(potential_delegations)

        min_weight_delegate = potential_delegations[0]
        min_weight_voter = self.transitive_delegations[min_weight_delegate]
        min_weight = self.voter_weights[min_weight_voter]
        for delegate in potential_delegations[1:]:
            voter = self.transitive_delegations[delegate]
            weight = self.voter_weights[voter]
            if weight < min_weight:
                min_weight_delegate = delegate
                min_weight_voter = voter
                min_weight = weight

        self.delegations.append(min_weight_delegate)
        self.transitive_delegations.append(min_weight_voter)
        self.voter_weights[min_weight_voter] += 1
        self.voter_weights.append(0)

        self._check_assertions()

    def get_delegations(self, time_out=None):
        return self.delegations


class GeneralizedPowerOfChoice(ConfluentMechanism):
    """Uses the power of choice on nodes in topological order of the graph of strongly connected components."""

    PLOT_COLOR = "#FF9800"
    PLOT_LABEL = "generalized greedy power of choice"
    PLOT_ABBREVIATION = "t"
    PLOT_PATTERN = "solid"

    def get_delegations(self, time_out=None):
        num_nodes = len(self.graph.potential_delegations)
        delegations = [None for _ in range(num_nodes)]
        transitive_delegations = [None for _ in range(num_nodes)]
        weights = [0 for _ in range(num_nodes)]

        counter = 0
        dfs_low = [None for _ in range(num_nodes)]
        dfs_num = [None for _ in range(num_nodes)]  # counter at visiting node, None if unvisited
        dfs_stack = []
        in_stack = [False for _ in range(num_nodes)]  # visited[n] iff n in dfs_stack

        def dfs(node):
            # Tarjan's SCC algorithm
            nonlocal delegations, dfs_low, dfs_num, counter, dfs_stack
            dfs_low[node] = counter
            dfs_num[node] = counter
            counter += 1
            dfs_stack.append(node)
            in_stack[node] = True

            if not self.graph.is_voter(node):
                for neighbor in self.graph.potential_delegations[node]:
                    if dfs_num[neighbor] is None:
                        dfs(neighbor)
                        dfs_low[node] = min(dfs_low[node], dfs_low[neighbor])
                    elif in_stack[neighbor]:
                        dfs_low[node] = min(dfs_low[node], dfs_num[neighbor])

            if dfs_low[node] == dfs_num[node]:  # New SCC found with node as root
                index = dfs_stack.index(node)
                scc = dfs_stack[index:]
                dfs_stack = dfs_stack[:index]
                for n in scc:
                    in_stack[n] = False
                for _ in range(len(scc)):  # This would be more efficient as a BFS, should not matter for our graphs
                    for n in scc:
                        if transitive_delegations[n] is None:
                            if self.graph.is_voter(n):
                                transitive_delegations[n] = n
                                weights[n] = 1
                                break
                            if not self.graph.is_voter(n):
                                min_delegation_weight = inf
                                min_delegation = None
                                for m in self.graph.potential_delegations[n]:
                                    if transitive_delegations[m] is not None:
                                        transitive = transitive_delegations[m]
                                        if weights[transitive] < min_delegation_weight:
                                            min_delegation_weight = weights[transitive]
                                            min_delegation = m
                                if min_delegation is not None:
                                    delegations[n] = min_delegation
                                    transitive_delegations[n] = transitive_delegations[min_delegation]
                                    weights[transitive_delegations[n]] += 1
                                    break
                assert (transitive_delegations[n] is not None for n in scc)

        for i in range(num_nodes):
            if dfs_num[i] is None:
                dfs(i)

        assert ((delegations[n] is None) == (self.graph.is_voter(n)) for n in range(num_nodes))

        return delegations


class GreedyRandomDelegation(ConfluentMechanism):
    PLOT_COLOR = "#F44336"
    PLOT_ABBREVIATION = "r"
    PLOT_LABEL = "greedy random"
    PLOT_PATTERN = "solid"

    def __init__(self, graph):
        super().__init__(graph)
        self.delegations = [None]

    def notify_of_added_voting_node(self):
        self.delegations.append(None)

    def notify_of_added_delegating_node(self, potential_delegations):
        self.delegations.append(choice(potential_delegations))

    def get_delegations(self, time_out=None):
        return self.delegations


def generate_aliased_mechanism(mechanism, plot_label, plot_pattern):
    class AliasedMechanism(mechanism):
        PLOT_LABEL = plot_label
        PLOT_ABBREVIATION = plot_label
        PLOT_PATTERN = plot_pattern

    return AliasedMechanism
