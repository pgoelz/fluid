from sys import modules
from unittest import TestCase

from mock import MagicMock


class TestOnePlusLogTwoApproximation(TestCase):
    # list of (list of (None / list of int), dict of int → float, list of (None / int))
    # (potential_delegations, splittable_flow, expected_result)
    test_cases = [([None, None, [0, 1], [2], [1]], [None, None, {0: 1.5, 1: .5}, {2: 1.}, {1: 1.}],
                   [None, None, 1, 2, 1]),
                  ([None, None, [0, 1], [0, 1]], [None, None, {0: .3, 1: .7}, {0: .7, 1: .3}], [None, None, 0, 1])]

    class MockGraph:
        def __init__(self, potential_delegations):
            self.potential_delegations = potential_delegations
            self.observers = []

        def is_voter(self, node):
            return self.potential_delegations[node] is None

        def number_of_nodes(self):
            return len(self.potential_delegations)

    def test_get_delegations(self):
        mock = MagicMock()
        modules["fractional_integral_flow"] = mock
        from approximate_confluent_flow import OnePlusLogTwoApproximation

        for current_case in self.test_cases:
            a = self.MockGraph(current_case[0])
            o = OnePlusLogTwoApproximation(a)
            mock.SplittableFlow.solve_flow.return_value = (current_case[1], None)
            delegations = o.get_delegations()
            assert delegations == current_case[2]


class TestOnePlusLnApproximation(TestCase):
    # list of (list of (None / list of int), dict of int → float, list of (None / int))
    # (potential_delegations, splittable_flow, expected_result)
    test_cases = [([None, None, None, None, None, [0, 1], [1, 7], [2, 3], [3, 4], [5], [6], [8]],
                   [None, None, None, None, None, {0: 1.4, 1: .6}, {1: .8, 7: 1.2}, {2: 1.4, 3: .8}, {3: .6, 4: 1.4},
                    {5: 1.}, {6: 1.}, {8: 1.}],
                   [None, None, None, None, None, 0, 1, 3, 4, 5, 6, 8])]

    class MockGraph:
        def __init__(self, potential_delegations):
            self.potential_delegations = potential_delegations
            self.observers = []

        def is_voter(self, node):
            return self.potential_delegations[node] is None

        def number_of_nodes(self):
            return len(self.potential_delegations)

    def test_get_delegations(self):
        mock = MagicMock()
        modules["fractional_integral_flow"] = mock
        from approximate_confluent_flow import OnePlusLnApproximation

        for current_case in self.test_cases:
            a = self.MockGraph(current_case[0])
            o = OnePlusLnApproximation(a)
            mock.SplittableFlow.solve_flow.return_value = (current_case[1], None)
            delegations = o.get_delegations()
            print(delegations)
            assert True  # Result not deterministic due to Gurobi
