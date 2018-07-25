from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from subprocess import Popen, PIPE
from numpy.random import seed
from simulations import Graph

if __name__ == "__main__":
    parser = ArgumentParser(description=("Generate example graphs via preferential attachment and render them with "
                                         "GraphViz."),
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('time', metavar='T', type=int,
                        help='number of agents > 0 (int)')
    parser.add_argument('-g', type=float, default=1.0,
                        help='gamma (float)')
    parser.add_argument('-d', type=float, default=0.5,
                        help='d \in (0,1) (float)')
    parser.add_argument('-k', type=int, default=0.5,
                        help='k > 0 (int)')
    parser.add_argument('-sd', type=int, default=0,
                        help='random seed (int)')
    parser.add_argument('-o', type=str, default=None,
                        help='output path for plot, defaulting to "/data/graphs/DESCRIPTION.pdf" (str)')
    args = parser.parse_args()

    time = args.time
    gamma = args.g
    d = args.d
    k = args.k
    sd = args.sd
    plot_path = args.o

    if plot_path is None:
        plot_path = f"data/graphs/k{k}d{round(d * 100)}g{round(gamma * 100)}.pdf"

    seed(sd)
    a = Graph(gamma, d, k)
    for _ in range(time - 1):
        a.add_node()
    dot = Popen(["dot", "-Tpdf", "-Kdot", "-o", plot_path],
                stdin=PIPE)
    # unflatten stacks voters without delegations to make the aspect ratio less wide
    # Change parameter 3 to change stacking height
    unf = Popen(["unflatten", "-c", "3"], stdin=PIPE, stdout=dot.stdin)
    unf.communicate(input=a.to_dot().encode("ascii"))
