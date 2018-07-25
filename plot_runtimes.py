from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from math import ceil
from time import process_time

from matplotlib import pyplot as plt, rc
from numpy.random import seed

from mechanism_names import parse_mechanisms, describe_mechanisms
from plot_smoothened_traces import Setting
from simulations import Graph

MECHANISM_TIMEOUT = 8 * 60


def compare_runtimes(settings, time, random_seed, log_path=None, plot_path=None):
    """
    Args:
        settings (list of Setting): Description s of a setting
        time (int): total time steps to run
        random_seed (int): seed for randomness
        log_path (string / None): Desired path for log. Defaults to data/logs/TITLE.csv, where TITLE includes parameters
        plot_path (string / None): Desired path for graphics file. PDF extension is supported, other file formats may
                                  also work depending on matplotlib. Defaults to data/plots/TITLE.pdf
    """

    title = f"tsmo_T{time}_sd{random_seed}"
    for s in settings:
        title += (f"_({''.join(m.PLOT_ABBREVIATION for m in s.mechanisms)}_g{round(s.gamma * 100)}_k{s.outdegree}_"
                  f"d{round(s.d * 100)}_sz{s.step_size}_s{s.smoothing})")
    if log_path is None:
        log_path = f"data/logs/{title}.csv"
    if plot_path is None:
        plot_path = f"data/plots/{title}.pdf"

    plt.figure(figsize=(6.4, 4.8))

    fonts = {'family': 'serif', 'serif': ['Libertine']}
    rc('font', **fonts)
    rc('text', usetex=True)

    with open(log_path, 'w') as file:
        file.write(f"Runtimes: settings={settings}, T={time}, random_seed={random_seed}\n")

        for s in settings:
            seed(random_seed)

            runtime_history_sum = [[0 for _ in range(ceil(time / s.step_size))] for _ in s.mechanisms]

            for iteration in range(s.smoothing):
                print(f"Iteration {iteration + 1} out of {s.smoothing}")

                elapsed_time = [0. for _ in s.mechanisms]
                graph = Graph(s.gamma, s.d, s.outdegree)

                mechanisms = [observer_class(graph) for observer_class in s.mechanisms]

                tick = -1
                for t in range(1, time + 1):
                    if t != 1:
                        graph.add_node()

                    if (t - 1) % s.step_size == 0:
                        tick += 1
                        for i, mechanism in enumerate(mechanisms):
                            if tick >= len(runtime_history_sum[i]):
                                continue

                            time_out = False
                            begin = process_time()
                            try:
                                mechanism.get_delegations(time_out=MECHANISM_TIMEOUT - elapsed_time[i])
                            except TimeoutError:
                                time_out = True
                            duration = process_time() - begin
                            elapsed_time[i] += duration
                            if elapsed_time[i] >= MECHANISM_TIMEOUT:
                                time_out = True

                            if time_out:
                                runtime_history_sum[i] = runtime_history_sum[i][:tick]
                                print(f"Mechanism {mechanism.PLOT_LABEL} timed out in iteration {iteration + 1} and "
                                      f"at time {elapsed_time[i]} s.")
                                continue
                            runtime_history_sum[i][tick] += duration

            for i, mechanism in enumerate(s.mechanisms):
                if len(runtime_history_sum[i]) == 0:
                    print(f"Nothing to plot for {mechanism.PLOT_LABEL}, all iterations timed out.")
                    continue
                n = [x * s.step_size + 1 for x in range(len(runtime_history_sum[i]))]
                average_runtime = [time / s.smoothing for time in runtime_history_sum[i]]
                plt.plot(n, average_runtime, color=mechanism.PLOT_COLOR, label=mechanism.PLOT_LABEL,
                         linestyle=mechanism.PLOT_PATTERN)

    plt.legend(loc=2)
    plt.ylabel('average runtime (s)')
    plt.xlabel('number of nodes')
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.savefig(plot_path, bbox_inches='tight')


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('max_number', metavar='M', type=int,
                        help='maximum number of nodes generated (int)')
    parser.add_argument('-g', type=float, default=1,
                        help='gamma (float)')
    parser.add_argument('-k', type=int, default=2,
                        help='k > 0 (int)')
    parser.add_argument('-d', type=float, default=0.5,
                        help='d ∈ (0,1) (float)')
    parser.add_argument('-sz', type=int, default=1,
                        help='value of step size > 0 (int)')
    parser.add_argument('-sm', type=int, default=10,
                        help='number of iterations for smoothing (int)')
    parser.add_argument('-sd', type=int, default=0,
                        help='value of seed (int)')
    parser.add_argument('-m', type=str, default='prcsAa',
                        help='mechanisms to use:\n' + describe_mechanisms(False))
    parser.add_argument('-ol', type=str, default=None,
                        help='write path for log')
    parser.add_argument('-o', type=str, default=None,
                        help='write path for plot')
    args = parser.parse_args()

    max_number = args.max_number
    gamma = args.g
    k = args.k
    d = args.d
    step_size = args.sz
    smoothing = args.sm
    random_seed = args.sd
    log_path = args.ol
    plot_path = args.o
    mechanisms = parse_mechanisms(args.m, False)

    print(args)

    setting = Setting(mechanisms, gamma, k, d, step_size, smoothing)
    compare_runtimes([setting], max_number, random_seed, log_path, plot_path)
