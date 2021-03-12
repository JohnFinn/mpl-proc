#!/usr/bin/env python3
import subprocess
from pathlib import Path

class AnimPlot:

    def __init__(self, *labels):
        self.process = subprocess.Popen(['plot.py', *labels], stdin=subprocess.PIPE)

    def add(self, *nums):
        self.process.stdin.write(b' '.join([str(i).encode() for i in nums]))
        self.process.stdin.write(b'\n')
        self.process.stdin.flush()
