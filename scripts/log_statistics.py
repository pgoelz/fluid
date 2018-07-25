"""Extracts some aggregate information from log traces.

Usage is quite hacky:
For example, let's say that we ran the example from Figure 1d of the paper:
$ python3 -O plot_smoothened_traces.py -g 1.0 -d 0.5 -sm 100 -sz 50 -sd 0 -o data/plots/fig1d.pdf -ol data/logs/fig1d.csv 5000
Now, data/logs/fig1d.csv has the following structure:

Line 1:                   Parameter information
Line 2 – 5,001:           First run for k=1
Line 5,002 – 10,001:      Second run for k=1
…
Line 495,002 – 500,001:   100th run for k=1
Line 500,002 – 505,001:   First run for k=2
…
Line 995,002 – 1,000,001: 100th run for k=2

We can get information on the first run for k=1 by executing

$ sed -n '500002,505001p' data/logs/fig1d.csv | python3 scripts/log_statistics.py
> num_initial_vertices = 1
> num_voters = 2409
> num_delegators = 2591
> num_no_choice_delegators = 5
> total_nodes = 5000
> double_to_most_frequent = 1
> min_k = 2
> max_k = 2
"""

from ast import literal_eval
from collections import Counter
from fileinput import input
from math import inf

if __name__ == "__main__":
    num_initial_vertices = 0
    num_voters = 0
    num_no_choice_delegators = 0
    total_nodes = 0
    min_k = inf
    max_k = -inf

    double_to_most_frequent = 0
    most_frequent = Counter()

    for line in input():
        items = line.strip().split("\t")
        assert(len(items) >= 2)
        try:
            int(items[0])
        except ValueError:
            assert False

        event = items[1]
        if event == "Initial voter":
            num_initial_vertices += 1
            num_voters += 1

            if len(most_frequent) > 0:
                double_to_most_frequent += most_frequent.most_common(1)[0][1]
                most_frequent = Counter()
        elif event == "New voter":
            num_voters += 1
        else:
            delegations = literal_eval(event)
            assert len(delegations) > 0

            min_k = min(min_k, len(delegations))
            max_k = max(max_k, len(delegations))

            if all(d == delegations[0] for d in delegations[1:]):
                num_no_choice_delegators += 1
                most_frequent.update([delegations[0]])

        total_nodes += 1

    if len(most_frequent) > 0:
        double_to_most_frequent += most_frequent.most_common(1)[0][1]

    print(f"num_initial_vertices = {num_initial_vertices}\n"
          f"num_voters = {num_voters}\n"
          f"num_delegators = {total_nodes - num_voters}\n"
          f"num_no_choice_delegators = {num_no_choice_delegators}\n"
          f"total_nodes = {total_nodes}\n"
          f"double_to_most_frequent = {double_to_most_frequent}\n"
          f"min_k = {min_k}\n"
          f"max_k = {max_k}")
