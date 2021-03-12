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
    plt.plot([], [], label=name)[0] for name in sys.argv[1:]
]

y_data = [[] for _ in sys.argv[1:]]
max_x = 1
crt_lim = 1

def init():
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 20)
    return lines

def update(nums):
    global crt_lim
    global max_x
    max_x += 1
    if max_x >= crt_lim:
        crt_lim *= 8
        ax.set_xlim(0, crt_lim)

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
        res = poller.poll(0)
        if res:
            line = input()
            nums = [float(i) for i in line.split()]
            update(nums)
            fig.canvas.draw()
            fig.canvas.flush_events()
        else:
            fig.canvas.flush_events()
            time.sleep(0.01)
