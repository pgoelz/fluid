#!/usr/bin/env bash
export GUROBI_SINGLE_THREAD=1 # Prevent Gurobi from running in parallel for making running times more reproducible
python3 -O plot_smoothened_traces.py -g 0.5 -d 0.25 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig9a.pdf -ol data/logs/fig9a.csv 5000 # Fig. 9a
python3 -O plot_smoothened_traces.py -g 0.5 -d 0.5 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig9b.pdf -ol data/logs/fig9b.csv 5000 # Fig. 9b
python3 -O plot_smoothened_traces.py -g 0.5 -d 0.75 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig9c.pdf -ol data/logs/fig9c.csv 5000 # Fig. 9c
python3 -O plot_smoothened_traces.py -g 2.0 -d 0.5 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig10.pdf -ol data/logs/fig10.csv 5000 # Fig. 10
python3 -O plot_smoothened_traces.py -g 1.25 -d 0.25 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig11a.pdf -ol data/logs/fig11a.csv 5000 # Fig. 11a
python3 -O plot_smoothened_traces.py -g 1.5 -d 0.25 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig11b.pdf -ol data/logs/fig11b.csv 5000 # Fig. 11b
python3 -O plot_smoothened_traces.py -g 1.25 -d 0.5 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig11c.pdf -ol data/logs/fig11c.csv 5000 # Fig. 11c
python3 -O plot_smoothened_traces.py -g 1.5 -d 0.5 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig11d.pdf -ol data/logs/fig11d.csv 5000 # Fig. 11d
python3 -O plot_smoothened_traces.py -g 1.25 -d 0.75 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig11e.pdf -ol data/logs/fig11e.csv 5000 # Fig. 11e
python3 -O plot_smoothened_traces.py -g 1.5 -d 0.75 -sm 100 -sz 50 -sd 0 -m npc -o data/plots/fig11f.pdf -ol data/logs/fig11f.csv 5000 # Fig. 11f
python3 -O plot_smoothened_traces.py -g 0.0 -d 0.25 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12a.pdf -ol data/logs/fig12a.csv 2000 # Fig. 12a
python3 -O plot_smoothened_traces.py -g 0.0 -d 0.5 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12b.pdf -ol data/logs/fig12b.csv 2000 # Fig. 12b
python3 -O plot_smoothened_traces.py -g 0.0 -d 0.75 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12c.pdf -ol data/logs/fig12c.csv 2000 # Fig. 12c
python3 -O plot_smoothened_traces.py -g 0.5 -d 0.25 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12d.pdf -ol data/logs/fig12d.csv 2000 # Fig. 12d
python3 -O plot_smoothened_traces.py -g 0.5 -d 0.5 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12e.pdf -ol data/logs/fig12e.csv 2000 # Fig. 12e
python3 -O plot_smoothened_traces.py -g 0.5 -d 0.75 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12f.pdf -ol data/logs/fig12f.csv 2000 # Fig. 12f
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.25 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12g.pdf -ol data/logs/fig12g.csv 2000 # Fig. 12g
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.5 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12h.pdf -ol data/logs/fig12h.csv 2000 # Fig. 12h
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.75 -sm 100 -sz 50 -sd 0 -m nrp -o data/plots/fig12i.pdf -ol data/logs/fig12i.csv 2000 # Fig. 12i
python3 -O plot_single_trace.py -g 1.0 -k 2 -d 0.5 -t 1000 -sz 1 -sd 0 -m cs -o data/plots/fig13a.pdf -ol data/logs/fig13a.csv # Fig. 13a
python3 -O plot_smoothened_traces.py -g 1.0 -d 0.5 -sm 100 -sz 50 -sd 0 -m cs -o data/plots/fig13b.pdf -ol data/logs/fig13b.csv 5000 # Fig. 13b
python3 -O plot_distribution_at_time.py -g 0.0 -d 0.25 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig14a.pdf # Fig. 14a
python3 -O plot_distribution_at_time.py -g 0.0 -d 0.25 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig14b.pdf # Fig. 14b
python3 -O plot_distribution_at_time.py -g 0.0 -d 0.5 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig15a.pdf # Fig. 15a
python3 -O plot_distribution_at_time.py -g 0.0 -d 0.5 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig15b.pdf # Fig. 15b
python3 -O plot_distribution_at_time.py -g 0.0 -d 0.75 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig16a.pdf # Fig. 16a
python3 -O plot_distribution_at_time.py -g 0.0 -d 0.75 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig16b.pdf # Fig. 16b
python3 -O plot_distribution_at_time.py -g 0.5 -d 0.25 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig17a.pdf # Fig. 17a
python3 -O plot_distribution_at_time.py -g 0.5 -d 0.25 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig17b.pdf # Fig. 17b
python3 -O plot_distribution_at_time.py -g 0.5 -d 0.5 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig18a.pdf # Fig. 18a
python3 -O plot_distribution_at_time.py -g 0.5 -d 0.5 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig18b.pdf # Fig. 18b
python3 -O plot_distribution_at_time.py -g 0.5 -d 0.75 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig19a.pdf # Fig. 19a
python3 -O plot_distribution_at_time.py -g 0.5 -d 0.75 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig19b.pdf # Fig. 19b
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.25 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig20a.pdf # Fig. 20a
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.25 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig20b.pdf # Fig. 20b
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.5 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig21a.pdf # Fig. 21a
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.5 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig21b.pdf # Fig. 21b
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.75 -t 500 -num 1000 -sd 0 -m rpacs -o data/plots/fig22a.pdf # Fig. 22a
python3 -O plot_distribution_at_time.py -g 1.0 -d 0.75 -t 500 -num 1000 -sd 0 -m pacs -o data/plots/fig22b.pdf # Fig. 22b
python3 -O plot_runtimes.py -g 0.0 -k 2 -d 0.25 -sz 100 -sm 20 -sd 0 -m tac -o data/plots/fig23a.pdf -ol data/logs/fig23a.csv 10000 # Fig. 23a
python3 -O plot_runtimes.py -g 1.0 -k 2 -d 0.25 -sz 100 -sm 20 -sd 0 -m tac -o data/plots/fig23b.pdf -ol data/logs/fig23b.csv 10000 # Fig. 23b
python3 -O plot_runtimes.py -g 0.0 -k 2 -d 0.5 -sz 100 -sm 20 -sd 0 -m tac -o data/plots/fig23c.pdf -ol data/logs/fig23c.csv 10000 # Fig. 23c
python3 -O plot_runtimes.py -g 1.0 -k 2 -d 0.5 -sz 100 -sm 20 -sd 0 -m tac -o data/plots/fig23d.pdf -ol data/logs/fig23d.csv 10000 # Fig. 23d
python3 -O plot_runtimes.py -g 0.0 -k 2 -d 0.75 -sz 100 -sm 20 -sd 0 -m tac -o data/plots/fig23e.pdf -ol data/logs/fig23e.csv 10000 # Fig. 23e
python3 -O plot_runtimes.py -g 1.0 -k 2 -d 0.75 -sz 100 -sm 20 -sd 0 -m tac -o data/plots/fig23f.pdf -ol data/logs/fig23f.csv 10000 # Fig. 23f
