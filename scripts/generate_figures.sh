#!/usr/bin/env bash
export GUROBI_SINGLE_THREAD=1 # Prevent Gurobi from running in parallel for making running times more reproducible
python3 -O graph_examples.py -g 0.0 -d 0.5 -k 2 -sd 0 -o data/plots/fig1a.pdf 50 # Fig. 1a
python3 -O graph_examples.py -g 1.0 -d 0.5 -k 2 -sd 0 -o data/plots/fig1b.pdf 50 # Fig. 1b
python3 -O plot_smoothened_traces.py -g 0.0 -d 0.25 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig2a.pdf -ol data/logs/fig2a.csv 5000 # Fig. 2a
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.25 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig2b.pdf -ol data/logs/fig2b.csv 5000 # Fig. 2b
python3 -O plot_smoothened_traces.py -g 0.0 -d 0.5 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig2c.pdf -ol data/logs/fig2c.csv 5000 # Fig. 2c
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.5 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig2d.pdf -ol data/logs/fig2d.csv 5000 # Fig. 2d
python3 -O plot_smoothened_traces.py -g 0.0 -d 0.75 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig2e.pdf -ol data/logs/fig2e.csv 5000 # Fig. 2e
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.75 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig2f.pdf -ol data/logs/fig2f.csv 5000 # Fig. 2f
python3 -O different_k.py -g 1.0 -d 0.5 -sm 100 -sz 10 -sd 0 -o data/plots/fig3.pdf -ol data/logs/fig3.csv 1000 # Fig. 3
python3 -O plot_varying_outdegree.py -g 1.0 -d 0.5 -kp 0.0 0.2 0.4 0.6 0.8 1.0 -sm 100 -sz 50 -sd 0 -o data/plots/fig4.pdf -ol data/logs/fig4.csv 5000 # Fig. 4
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.5 -t 100 -num 1000 -sd 0 -m rpac -o data/plots/fig5a.pdf # Fig. 5a
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.5 -t 500 -num 1000 -sd 0 -m pac -o data/plots/fig5b.pdf # Fig. 5b
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.5 -sm 100 -sz 50 -sd 0 -m rpac -o data/plots/fig6.pdf -ol data/logs/fig6.csv -pw 6.4 -ph 4.8 2000 # Fig. 6
python3 -O plot_runtimes.py -g 1.0 -k 2 -d 0.5 -sz 100 -sm 20 -sd 0 -m tac -o data/plots/fig7.pdf -ol data/logs/fig7.csv 10000 # Fig. 7
