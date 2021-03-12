#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import itertools
import sys

class TypedEventSource:

    def __init__(self):
        self.callbacks = set()

    def add_callback(self, callback):
        self.callbacks.add(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)

    def start(self):
        pass

    def stop(self):
        pass


fig, ax = plt.subplots()

x_data = []
lines = [
    plt.plot([], [], label=name)[0] for name in sys.argv[1:]
]

y_data = [[] for _ in sys.argv[1:]]
max_x = 1

def init():
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    return lines

def update(nums):
    global max_x
    max_x += 1
    x_data.append(max_x)
    # ax.set_xlim(0, frame)
    # ax.set_ylim(min_y * 1.1, max_y * 1.1)
    for next_num, ydata, ln in zip(nums, y_data, lines):
        ydata.append(next_num)
        ln.set_data(x_data, ydata)

    return lines

def read_lines():
    for line in sys.stdin:
        yield [float(i) for i in line.split()]


if __name__ == '__main__':
    ani = FuncAnimation(fig, update, frames=read_lines(), interval=0, repeat=True, # deletes the whole plot when resizing
                    init_func=init, blit=True)
    plt.legend()
    plt.show()
