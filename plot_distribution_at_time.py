from argparse import ArgumentParser
from math import floor, ceil

from matplotlib import pyplot as plt, rc
from matplotlib.ticker import FormatStrFormatter
from numpy import arange
from numpy import median
from numpy.random import seed

from mechanism_names import parse_mechanisms, describe_mechanisms
from simulations import Graph


def plot_distribution_at_time(mechanism_classes, gamma, outdegree, d, time, num_runs, random_seed, plot_path=None):
    """Plot a histogram of maximum weight frequencies at time T over many runs.

    Args:
        mechanism_classes (list of classes inheriting from Mechanism)
        gamma (float): gamma in the graph model
        outdegree (int): k in the graph model
        d (float): probability of delegating in the graph model
        time (int): total time steps to run
        num_runs (int): number of runs at which to compute max degree at time T
        random_seed (int): seed for randomness
        plot_path (string / None): Output path for graphic. File extensions as allowed by matplotlib, e.g. pdf.
    """

    mechanism_abbrevs = ""
    for mechanism_class in mechanism_classes:
        mechanism_abbrevs += mechanism_class.PLOT_ABBREVIATION

    title = (f"hist_{mechanism_abbrevs}_g{round(gamma * 100)}_k{outdegree}_d{round(d * 100)}_T{time}_num{num_runs}"
             f"_sd{random_seed}")
    if plot_path is None:
        plot_path = f"data/histplots/{title}.pdf"

    rc('font', **{'family': 'serif', 'serif': ['Libertine']})
    rc('text', usetex=True)

    seed(random_seed)

    mechanisms_history = {observer_class.PLOT_ABBREVIATION: [] for observer_class in mechanism_classes}

    assert num_runs > 0
    for i in range(num_runs):
        graph = Graph(gamma, d, outdegree)
        mechanisms = [observer_class(graph) for observer_class in mechanism_classes]
        print(i)
        for t in range(2, time + 1):
            graph.add_node()
        for mechanism in mechanisms:
            delegations = mechanism.get_delegations()
            max_weight = mechanism.max_weight_from_delegations(delegations)
            mechanisms_history[mechanism.PLOT_ABBREVIATION].append(max_weight)

    all_max_weight_histories = []
    mechanism_names = []
    for mechanism in mechanisms_history:
        all_max_weight_histories.append(mechanisms_history[mechanism])
    for mechanism in mechanisms:
        mechanism_names.append(mechanism.PLOT_LABEL)

    min_weight = floor(min(min(all_max_weight_histories)))
    max_weight = ceil(max(max(all_max_weight_histories)))

    # plot
    num_plots = len(all_max_weight_histories)

    fig, ax = plt.subplots(num_plots, sharex=True, sharey=True, figsize=(6.4, 3.2))

    for i in range(num_plots):
        ax[i].hist(all_max_weight_histories[i], normed=1, bins=arange(min_weight - 0.5, max_weight + 1.5, 1),
                   color=mechanism_classes[i].PLOT_COLOR, label=mechanism_classes[i].PLOT_LABEL)
        ax[i].axvline(median(all_max_weight_histories[i]), color='black', linestyle='solid', linewidth=1)
        ax[i].legend(loc=1)
        ax[i].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax = fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.xlabel('maximum weight')
    plt.ylabel('frequency')
    ax.yaxis.labelpad = 10
    plt.savefig(plot_path, bbox_inches='tight')


if __name__ == "__main__":
    parser = ArgumentParser(description='Inputs.')
    parser.add_argument('-g', type=float, nargs='+', default=[1],
                        help='values of gamma (list of float)')
    parser.add_argument('-k', type=int, nargs='+', default=[2],
                        help='values of k > 0 (list of int)')
    parser.add_argument('-d', type=float, nargs='+', default=[0.5],
                        help='values of d \in (0,1) (list of float)')
    parser.add_argument('-t', type=int, default=100,
                        help='value of T > 0 (int)')
    parser.add_argument('-num', type=int, default=10,
                        help='value of num iters > 0 (int)')
    parser.add_argument('-sd', type=int, default=0,
                        help='value of seed (int)')
    parser.add_argument('-m', type=str, default='prcsAa',
                        help='mechanisms to use:\n' + describe_mechanisms(False))
    parser.add_argument('-o', type=str, default=None,
                        help='write path for plot')

    args = parser.parse_args()

    gammas = args.g
    ks = args.k
    ds = args.d
    time = args.t
    num_runs = args.num
    random_seed = args.sd
    plot_path = args.o
    mechanism_classes = parse_mechanisms(args.m, False)

    print(args)

    for gamma in gammas:
        for d in ds:
            for k in ks:
                plot_distribution_at_time(mechanism_classes, gamma, k, d, time, num_runs, random_seed, plot_path)
