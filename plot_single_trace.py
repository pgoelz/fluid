from argparse import ArgumentParser
from math import ceil

from matplotlib import pyplot as plt, rc
from numpy.random import seed

from mechanism_names import parse_mechanisms, describe_mechanisms
from simulations import Graph, ProtocollingObserver


def compare_mechanisms_on_single_trace(mechanism_classes, gamma, outdegree, d, time, step_size, random_seed, log_path,
                                       plot_path):
    """
    Args:
        mechanism_classes (list of classes inheriting from Mechanism)
        gamma (float): gamma in the graph model
        outdegree (int): k in the graph model
        d (float): probability of delegating in the graph model
        time (int): total time steps to run
        step_size (int): increments in which to compute max degree
        random_seed (int): seed for randomness
        log_path (string / None): Desired path for log. Defaults to data/logs/TITLE.csv, where TITLE includes parameters
        plot_path (string / None): Desired path for graphics file. PDF extension is supported, other file formats may
                                  also work depending on matplotlib. Defaults to data/plots/TITLE.pdf
    """

    seed(random_seed)

    graph = Graph(gamma, d, outdegree)

    protocolist = ProtocollingObserver(graph)

    # Pair of mechanism and its max_weight history
    mechanisms = [(observer_class(graph), []) for observer_class in mechanism_classes]

    for mechanism, max_weight_history in mechanisms:
        delegations = mechanism.get_delegations()
        max_weight = mechanism.max_weight_from_delegations(delegations)
        assert max_weight == 1
        max_weight_history.append(max_weight)

    for t in range(2, time + 1):
        graph.add_node()
        if (t - 1) % step_size == 0:
            print(t)
            for mechanism, max_weight_history in mechanisms:
                delegations = mechanism.get_delegations()
                max_weight = mechanism.max_weight_from_delegations(delegations)
                max_weight_history.append(max_weight)

    # plot
    n = [x * step_size + 1 for x in range(ceil(time / step_size))]

    mechanism_abbrevs = ""
    for mechanism_class in mechanism_classes:
        mechanism_abbrevs += mechanism_class.PLOT_ABBREVIATION

    title = (f"plt_{mechanism_abbrevs}_g{round(gamma * 100)}_k{outdegree}_d{round(d * 100)}_T{time}_sz{step_size}_"
             f"sd{random_seed}")
    if log_path is None:
        log_path = f"data/logs/{title}.csv"
    if plot_path is None:
        plot_path = f"data/plots/{title}.pdf"

    rc('font', **{'family': 'serif', 'serif': ['Libertine']})
    rc('text', usetex=True)

    plt.figure()
    for mechanism, max_weight_history in mechanisms:
        plt.plot(n, max_weight_history, color=mechanism.PLOT_COLOR, label=mechanism.PLOT_LABEL)

    # plt.legend(loc=2, prop={'size': 8})
    plt.legend(loc=2)
    plt.ylabel('maximum weight')
    plt.xlabel('time')
    plt.savefig(plot_path, bbox_inches='tight')

    with open(log_path, "w") as file:
        file.write("t\tevent\t" + "\t".join(m.PLOT_LABEL for m in mechanism_classes) + "\n")
        for t in range(1, time + 1):
            file.write(f"{t}\t{protocolist.protocol[t - 1]}")
            if (t - 1) % step_size == 0:
                tick = (t - 1) // step_size
                for mechanism, max_weight_history in mechanisms:
                    file.write(f"\t{max_weight_history[tick]}")
            file.write("\n")


if __name__ == '__main__':
    parser = ArgumentParser(description='Inputs.')
    parser.add_argument('-g', type=float, nargs='+', default=[1],
                        help='values of gamma (list of float)')
    parser.add_argument('-k', type=int, nargs='+', default=[2],
                        help='values of k > 0 (list of int)')
    parser.add_argument('-d', type=float, nargs='+', default=[0.5],
                        help='values of d \in (0,1) (list of float)')
    parser.add_argument('-t', type=int, default=100,
                        help='value of T > 0 (int)')
    parser.add_argument('-sz', type=int, default=1,
                        help='value of step size > 0 (int)')
    parser.add_argument('-sd', type=int, default=0,
                        help='value of seed (int)')
    parser.add_argument('-m', type=str, default='prcsAa',
                        help='mechanisms to use:\n' + describe_mechanisms(False))
    parser.add_argument('-ol', type=str, default=None,
                        help='write path for log')
    parser.add_argument('-o', type=str, default=None,
                        help='write path for plot')

    args = parser.parse_args()

    gammas = args.g
    ks = args.k
    ds = args.d
    T = args.t
    step_size = args.sz
    random_seed = args.sd
    log_path = args.ol
    plot_path = args.o
    mechanisms = parse_mechanisms(args.m, False)

    print(args)

    for gamma in gammas:
        for d in ds:
            for k in ks:
                compare_mechanisms_on_single_trace(
                    mechanisms, gamma, k, d, T, step_size, random_seed, log_path, plot_path)
