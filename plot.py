#!/usr/bin/env python3
import time
import select
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import itertools
import sys

fig, ax = plt.subplots()

x_data = []
lines = [
    ax.plot([], [], label=name)[0] for name in sys.argv[1:]
]

y_data = [[] for _ in sys.argv[1:]]
max_x = 1
max_y, min_y = 0, 1
crt_lim = 1

def init():
    ax.set_xlim(0, 1)
    ax.set_ylim(10, 20)
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
        if poller.poll(0):
            while poller.poll(0):
                line = sys.stdin.readline()
                nums = [float(i) for i in line.split()]
                update(nums)
            fig.canvas.draw()
            fig.canvas.flush_events()
        else:
            fig.canvas.flush_events()
            time.sleep(0.01)
