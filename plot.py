#!/usr/bin/env python3
import argparse
import time
import select
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import itertools
import sys

parser = argparse.ArgumentParser()
parser.add_argument('labels', nargs='+')
parser.add_argument('--output', default='/dev/null')

args = parser.parse_args(sys.argv[1:])

fig: matplotlib.figure.Figure
ax: matplotlib.axes.Axes
fig, ax = plt.subplots()

x_data = []
lines = [
    ax.plot([], [], label=name)[0] for name in args.labels
]

y_data = [[] for _ in sys.argv[1:]]
max_x = 1
max_y, min_y = 1, 0
crt_lim = 1

def init():
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 20)
    return lines

def update(nums):
    global crt_lim
    global max_x
    global max_y
    global min_y
    max_x += 1
    crt_min_y, crt_max_y = min(nums), max(nums)
    if max_x >= crt_lim:
        crt_lim *= 2
        ax.set_xlim(0, crt_lim)
    if crt_max_y > max_y or crt_min_y < min_y:
        min_y = min(min_y, crt_min_y)
        max_y = max(crt_max_y, max_y)
        ax.set_ylim(top = max_y * 1.1, bottom = min_y * 1.1)

    x_data.append(max_x)
    # ax.set_ylim(min_y * 1.1, max_y * 1.1)
    for next_num, ydata, ln in zip(nums, y_data, lines):
        ydata.append(next_num)
        ln.set_data(x_data, ydata)

    return lines


if __name__ == '__main__':
    init()
    plt.legend()
    plt.show(block=False)

    poller = select.poll()
    poller.register(0, select.POLLIN)

    while True:
        do_break = False
        if poller.poll(0) == [(0, select.POLLHUP)]:
            break
        if poller.poll(0):
            while poller.poll(0) == [(0, select.POLLIN)]:
                line = sys.stdin.readline()
                if line == '':
                    do_break = True
                    break
                nums = [float(i) for i in line.split()]
                update(nums)
            if do_break:
                break
            fig.canvas.draw()
            fig.canvas.flush_events()
        else:
            fig.canvas.flush_events()
            time.sleep(0.01)

    fig.savefig(args.output)
