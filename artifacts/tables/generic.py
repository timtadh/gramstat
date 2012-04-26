#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess, functools, collections

from artifacts.reg import registration
from artifacts import sieve
import lib

def walktree(root, process=None, finalize=None):
    def default(*args):
        pass
    stack = list()
    if finalize is None: finalize = default
    if process is None: process = default
    #stack.append((root, functools.partial(finalize, root)))
    def visit(node, depth):
        process(node, depth)
        child_results = [visit(child, depth+1) for child in node.children]
        return finalize(node, depth, child_results)
    return visit(root, 1)

def walktrees(trees, process):
    for tree in trees:
        walktree(tree, process)

def save(path, table):
    s = '\n'.join( ', '.join(str(col) for col in row) for row in table )
    f = open(path, 'w')
    f.write(s)
    f.write('\n'*2)
    f.close()
    return table

@registration.register('table')
def prod_3grams(path, oldtable, tables, conf):
    trees = conf['trees']

    class Callback(object):

        def __init__(self, N):
            self.N = N
            self.grams = set()

        def __call__(self, node, depth, child_results):
            mygrams = set(((node.label, ), ))
            for child in child_results:
                for gram in child:
                    if len(gram) < self.N:
                        newgram = tuple([node.label] + list(gram))
                    else:
                        assert len(gram) == self.N
                        newgram = tuple([node.label] + list(gram[:-1]))
                    if len(newgram) == self.N:
                        self.grams.add(newgram)
                    mygrams.add(newgram)
            return mygrams

    grams = list()
    for tree in trees:
        cback = Callback(3)
        walktree(tree, finalize=cback)
        grams.append(cback.grams)

    table = [
      [X] + list(Z)
      for X, Y in enumerate(grams)
      for Z in Y
    ]
    for x in xrange(len(table[0])-1, -1, -1):
        table.sort(key=lambda row: row[x])
    save(path, table)
    return table


@registration.register('table')
def tree_number(path, oldtable, tables, conf):

    class callback(object):

        def __init__(self):
            self.acc = 1
            self.primes = sieve.find_primes()

        def __call__(self, node, depth):
            self.acc *= self.primes.next()**(len(node.children))

        def number(self):
            return self.acc

    numbers = list()
    trees = conf['trees']
    for tree in trees:
        c = callback()
        walktree(tree, c)
        numbers.append(c.number())

    table = tuple((i, n) for i, n in enumerate(numbers))
    save(path, table)
    return table


#@registration.register('table', uses=['coverage'])
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


