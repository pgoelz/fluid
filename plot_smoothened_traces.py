from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from math import ceil
from time import perf_counter

from matplotlib import pyplot as plt, rc
from numpy.random import seed

from mechanism_names import describe_mechanisms, parse_mechanisms
from simple_mechanisms import NoChoice
from simulations import Graph, ProtocollingObserver

MECHANISM_TIMEOUT = 30 * 60


class Setting:
    """
    Attributes:
        mechanisms (list of type): Classes inheriting from Mechanism
        gamma (float): Gamma for graph generation
        outdegree (int): Outdegree for graph generation
        d (float): Probability of delegation for graph generation
        step_size (int): increments in which to compute max degree
        smoothing (int): Number of iterations to average out
    """

    def __init__(self, mechanisms, gamma, outdegree, d, step_size, smoothing):
        self.mechanisms = mechanisms
        self.gamma = gamma
        self.outdegree = outdegree
        self.d = d
        self.step_size = step_size
        self.smoothing = smoothing

    def __str__(self):
        return (f"Setting(mechanisms={[m.__name__ for m in self.mechanisms]}, gamma={self.gamma}, "
                f"outdegree={self.outdegree}, d={self.d}, step_size={self.step_size}, smoothing={self.smoothing})")


def compare_smoothened_traces(settings, time, random_seed, log_path=None, plot_path=None, plot_width=6.4,
                              plot_height=3.2):
    """
    Args:
        settings (list of Setting): Description s of a setting
        time (int): Total time steps to run
        random_seed (int): Seed for randomness
        log_path (string / None): Desired path for log. Defaults to data/logs/TITLE.csv, where TITLE includes parameters
        plot_path (string / None): Desired path for graphics file. PDF extension is supported, other file formats may
                                  also work depending on matplotlib. Defaults to data/plots/TITLE.pdf
        plot_width (float): Width of figure in inches
        plot_height (float): Height of figure in inches
    """

    title = f"smo_T{time}_sd{random_seed}"
    for s in settings:
        title += (f"_({''.join(m.PLOT_ABBREVIATION for m in s.mechanisms)}_g{round(s.gamma * 100)}_k{s.outdegree}_"
                  f"d{round(s.d * 100)}_sz{s.step_size}_s{s.smoothing})")
    if log_path is None:
        log_path = f"data/logs/{title}.csv"
    if plot_path is None:
        plot_path = f"data/plots/{title}.pdf"

    plt.figure(figsize=(plot_width, plot_height))

    fonts = {'family': 'serif', 'serif': ['Libertine']}
    rc('font', **fonts)
    rc('text', usetex=True)

    with open(log_path, 'w') as file:
        file.write(f"Smoothened traces: settings={settings}, T={time}, random_seed={random_seed}\n")
        for s in settings:
            # Different iterations should be different for smoothing, but different settings might as well be as
            # reproducible as possible.
            seed(random_seed)

            print(s)
            max_weight_history_sum = [[0 for _ in range(ceil(time / s.step_size))] for _ in s.mechanisms]
            num_timeouts = [0 for _ in s.mechanisms]

            for iteration in range(s.smoothing):
                print(f"Iteration {iteration + 1} out of {s.smoothing}")

                elapsed_time = [0. for _ in s.mechanisms]
                time_out = [False for _ in s.mechanisms]
                graph = Graph(s.gamma, s.d, s.outdegree)

                max_weight_history_for_iteration = [[] for _ in s.mechanisms]

                protocolist = ProtocollingObserver(graph)

                mechanisms = [observer_class(graph) for observer_class in s.mechanisms]
                assert len(mechanisms) > 0

                # pull that into the loop
                tick = 0
                file.write("1\t" + protocolist.protocol[-1])
                for i, mechanism in enumerate(mechanisms):
                    delegations = mechanism.get_delegations()
                    max_weight = mechanism.max_weight_from_delegations(delegations)
                    assert max_weight == 1
                    max_weight_history_for_iteration[i].append(max_weight)
                    file.write("\t" + str(max_weight))
                file.write("\n")

                for t in range(2, time + 1):
                    graph.add_node()
                    file.write(f"{t}\t{protocolist.protocol[-1]}")
                    if (t - 1) % s.step_size == 0:
                        tick += 1
                        for i, mechanism in enumerate(mechanisms):
                            if time_out[i]:
                                continue

                            if elapsed_time[i] >= MECHANISM_TIMEOUT:
                                time_out[i] = True
                            else:
                                begin = perf_counter()
                                try:
                                    delegations = mechanism.get_delegations(
                                        time_out=MECHANISM_TIMEOUT - elapsed_time[i])
                                except TimeoutError:
                                    time_out[i] = True
                                elapsed_time[i] += perf_counter() - begin

                            if time_out[i]:
                                num_timeouts[i] += 1
                                print(f"Mechanism {mechanism.PLOT_LABEL} timed out for {num_timeouts[i]}th time in "
                                      f"iteration {iteration} after {elapsed_time[i]} s.")
                                assert len(max_weight_history_for_iteration[i]) == tick
                                n = [x * step_size + 1 for x in range(tick)]
                                plt.plot(n, max_weight_history_for_iteration[i], color=mechanism.PLOT_COLOR,
                                         label=f"{mechanism.PLOT_LABEL} (run {iteration + 1})",
                                         linestyle=mechanism.PLOT_PATTERN, alpha=1 / (num_timeouts[i] + 1))

                            max_weight = mechanism.max_weight_from_delegations(delegations)
                            max_weight_history_for_iteration[i].append(max_weight)
                            file.write("\t" + str(max_weight))
                    file.write("\n")

                for i, mechanism in enumerate(mechanisms):
                    if not time_out[i]:
                        for t in range(len(max_weight_history_for_iteration[i])):
                            max_weight_history_sum[i][t] += max_weight_history_for_iteration[i][t]

                file.flush()

            n = [x * s.step_size + 1 for x in range(ceil(time / s.step_size))]
            for i, mechanism in enumerate(s.mechanisms):
                if num_timeouts[i] == s.smoothing:
                    print(f"Nothing to plot for {mechanism.PLOT_LABEL}, all iterations timed out.")
                    continue
                max_weight_average = [weight_sum / (s.smoothing - num_timeouts[i]) for weight_sum in
                                      max_weight_history_sum[i]]
                assert len(n) == len(max_weight_average)
                plt.plot(n, max_weight_average, color=mechanism.PLOT_COLOR, label=mechanism.PLOT_LABEL,
                         linestyle=mechanism.PLOT_PATTERN)

    plt.legend(loc=2)
    plt.ylabel('average maximum weight')
    plt.xlabel('time')
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.savefig(plot_path, bbox_inches='tight')


if __name__ == '__main__':
    parser = ArgumentParser(description=("Draw smoothened traces of different mechanisms for k=2, or for k=1 if "
                                         f"specifying the mechanism '{NoChoice.PLOT_ABBREVIATION}'. For more advanced "
                                         "usage, use compare_smoothened_traces() directly!"),
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('time', metavar='T', type=int,
                        help='value of T > 0 (int)')
    parser.add_argument('-g', type=float, nargs='+', default=[1],
                        help='values of gamma (list of float)')
    parser.add_argument('-d', type=float, nargs='+', default=[0.5],
                        help='values of d \in (0,1) (list of float)')
    parser.add_argument('-sz', type=int, default=1,
                        help='value of step size > 0 (int)')
    parser.add_argument('-sm', type=int, default=10,
                        help='smoothing, i.e. number of traces to average over (int)')
    parser.add_argument('-sd', type=int, default=0,
                        help='value of seed (int)')
    parser.add_argument('-m', type=str, default='npc',
                        help='mechanisms to use:\n' + describe_mechanisms(True))
    parser.add_argument('-ol', type=str, default=None,
                        help='write path for log')
    parser.add_argument('-o', type=str, default=None,
                        help='write path for plot')
    parser.add_argument('-pw', type=float, default=6.2,
                        help='width of plot in inches (float)')
    parser.add_argument('-ph', type=float, default=3.2,
                        help='height of plot in inches (float)')

    args = parser.parse_args()

    time = args.time
    gammas = args.g
    ds = args.d
    step_size = args.sz
    random_seed = args.sd
    smoothing = args.sm
    log_path = args.ol
    plot_path = args.o
    single_mechanisms, mechanisms = parse_mechanisms(args.m, True)
    plot_width = args.pw
    plot_height = args.ph

    for gamma in gammas:
        for d in ds:
            settings = []
            if len(single_mechanisms) != 0:
                settings.append(Setting(single_mechanisms, gamma, 1, d, step_size, smoothing))
            if len(mechanisms) != 0:
                settings.append(Setting(mechanisms, gamma, 2, d, step_size, smoothing))
            compare_smoothened_traces(settings, time, random_seed, log_path, plot_path, plot_width, plot_height)
