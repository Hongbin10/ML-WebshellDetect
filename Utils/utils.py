# -*- coding: utf8 -*-

import os
import time
from rich.console import Console

def get_time():
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    return now

def get_file_size(fp):
    size = os.path.getsize(fp)
    if size >= 1000:
        size = str(round(size / 1000, 2)) + 'K'
    else:
        size = str(size) + 'B'
    return size

def timestamp2time(timestamp):
    timestruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timestruct)

def get_file_last_modify(fp):
    t = os.path.getmtime(fp)
    return timestamp2time(t)

if __name__ == '__main__':
    print = Console().print