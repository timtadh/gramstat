#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess

from reg import registration

def walktrees(trees, process):
    def walk(root):
        stack = list()
        stack.append(root)
        while stack:
            node = stack.pop()
            process(node)
            for child in node.children:
                stack.append(child)
    for tree in trees:
        walk(tree)

@registration.register('table')
def symbol_count(path, conf):
    fname = path + '.csv'
    symbols = dict()
    trees = conf['trees']

    walktrees(
        trees,
        lambda node:
            symbols.__setitem__(node.label, symbols.get(node.label, 0) + 1)
    )

    s = '\n'.join(
        ', '.join((name, str(count))) for name, count in symbols.iteritems()
    )

    f = open(fname, 'w')
    f.write(s)
    f.write('\n'*2)
    f.close()

@registration.register('table')
def non_term_count(path, conf):
    fname = path + '.csv'
    symbols = dict()
    trees = conf['trees']

    def callback(node):
        if node.children: symbols[node.label] = symbols.get(node.label, 0) + 1
    walktrees(trees, callback)

    s = '\n'.join(
        ', '.join((name, str(count))) for name, count in symbols.iteritems()
    )

    f = open(fname, 'w')
    f.write(s)
    f.write('\n'*2)
    f.close()

