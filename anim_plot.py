#!/usr/bin/env python3
import subprocess
from pathlib import Path

class AnimPlot:

    def __init__(self, *labels, output='/dev/null'):
        self.process = subprocess.Popen(['plot.py', '--output', output, *labels], stdin=subprocess.PIPE)

    def add(self, *nums):
        self.process.stdin.write(b' '.join([str(i).encode() for i in nums]) + b'\n')
        self.process.stdin.flush()

    def close(self):
        self.process.stdin.close()
        self.process.wait()
