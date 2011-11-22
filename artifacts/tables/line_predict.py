#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess, functools, collections

from artifacts.reg import registration
from artifacts import sieve
import lib

from generic import walktree, walktrees

@registration.register('table', uses=['coverage'])
def avg_filecov(path, oldtable, tables, conf):
    total_cov = dict()
    if oldtable is not None:
        for fname, total, avg in oldtable:
            total_cov[fname] = float(total)
    for cov_path, table in conf['coverage']:
        for fname, info in table.iteritems():
            Sum = total_cov.get(fname, 0.0)
            count = info['line_count']
            lines = info['executed_lines']
            if count:
                avg = len(lines)/float(count)
            else:
                avg = 1.0
            total_cov[fname] = Sum + avg
    table = [
        (fname, Sum, Sum/float(len(conf['trees'])))
        for fname, Sum in total_cov.iteritems()
    ]

    save(path, table)
    return table
