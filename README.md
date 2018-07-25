Read me
=======
This repository contains the simulation code for the paper

> Paul Gölz, Anson Kahng, Simon Mackenzie and Ariel D. Procaccia: The Fluid Mechanics of Liquid Democracy. 2018.

The paper is freely accessible at <http://procaccia.info/papers/fluid.pdf>.

Requirements
------------
- Python 3.6 (higher versions might work, but so far Gurobi does not support them)
- Gurobi with gurobipy python bindings (we used version 8.0.1)
- Matplotlib (2.2.2)
- Numpy (1.14.5)
- Mock (2.0.0): only required for unit tests in `test_approximate_confluent_flow.py`
- Graphviz (2.40.1): the `dot` and `unflatten` binaries should be available in PATH to generate example graphs in `graph_examples.py`.

For academic use, Gurobi provides free licenses at <http://www.gurobi.com/academia/for-universities>.

Replication of experiments in the paper
---------------------------------------
The figures from the body of the paper can be reproduced by running the script `scripts/generate_figures.sh`. The
produced plots can be found in `data/plots/`, named after the figure number, and most experiments also generate a log
in `data/logs/`. For more information on what the individual commands do and the meaning of the parameters, call the
individual python scripts with `-h`. Since script sets the environment variable `$GUROBI_SINGLE_THREAD`, our code
prevents Gurobi from spawning multiple threads. Without this variable, execution times will likely be faster, but less
reproducible. 

We expect the resulting graphics to be close to the ones found in our publication. In particular, the randomness seed
is fixed for all experiments. Nonetheless, details like the iteration order of dictionaries are not guaranteed to be
the same across different systems and versions of Python, which can lead to different results. Finally, running times
and time-outs heavily depend on the system. Our figures were generated on a MacBook Pro (2017) on MacOS 10.12.6 with a
3.1 GHz Intel Core i5 processor and 16 GB of RAM.

Questions
---------
For questions on the simulations, feel free to contact [Paul Gölz](https://paulgoelz.de) or
[Anson Kahng](https://www.cs.cmu.edu/~akahng/).
