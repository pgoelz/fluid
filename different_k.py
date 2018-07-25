from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from fractional_integral_flow import ConfluentFlow
from mechanism_names import MECHANISMS_LIST
from plot_smoothened_traces import compare_smoothened_traces, Setting
from simple_mechanisms import generate_aliased_mechanism

DASH_PATTERNS = ["solid", "dashed", (0, (1, 1)), (0, (3, 2, 1, 2)), (0, (1, 2.5))]


if __name__ == "__main__":
    parser = ArgumentParser(description=("Draw smoothened traces of optimal confluent flow for values of k from 1 "
                                         "to 5."),
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('time', metavar='T', type=int,
                        help='value of T > 0 (int)')
    parser.add_argument('-g', type=float, default=1.0,
                        help='value of gamma (float)')
    parser.add_argument('-d', type=float, default=0.5,
                        help='value of d \in (0,1) (float)')
    parser.add_argument('-sz', type=int, default=1,
                        help='value of step size > 0 (int)')
    parser.add_argument('-sm', type=int, default=10,
                        help='smoothing, i.e. number of traces to average over (int)')
    parser.add_argument('-sd', type=int, default=0,
                        help='value of seed (int)')
    parser.add_argument('-ol', type=str, default=None,
                        help='write path for log')
    parser.add_argument('-o', type=str, default=None,
                        help='write path for plot')
    args = parser.parse_args()

    time = args.time
    gamma = args.g
    d = args.d
    step_size = args.sz
    random_seed = args.sd
    smoothing = args.sm
    log_path = args.ol
    plot_path = args.o

    settings = []
    for k in range(1, 6):
        mechanism = generate_aliased_mechanism(ConfluentFlow, f"$k = {k}$", DASH_PATTERNS[k - 1])
        MECHANISMS_LIST.append(mechanism)
        settings.append(Setting([mechanism], gamma, k, d, step_size, smoothing))

    compare_smoothened_traces(settings, time, random_seed, log_path, plot_path)
