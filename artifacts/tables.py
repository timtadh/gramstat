#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess

from reg import registration


@registration.register('symbol_count', 'table')
def symbol_count(conf):
    fname = os.path.join(conf['outdir'], 'symbol_count.csv')
    symbols = dict()
    trees = conf['trees']
   
    def walk(node):
        stack = list()
        stack.append(node)
        while stack:
            node = stack.pop()
            symbols[node.label] = symbols.get(node.label, 0) + 1
            for child in node.children:
                stack.append(child)
    
    for tree in trees:
        walk(tree)
    
    s = '\n'.join(
        ', '.join((name, str(count))) for name, count in symbols.iteritems()
    )

    f = open(fname, 'w')
    f.write(s)
    f.write('\n'*2)
    f.close()

@registration.register('non_term_count', 'table')
def non_term_count(conf):
    fname = os.path.join(conf['outdir'], 'non_term_count.csv')
    symbols = dict()
    trees = conf['trees']
   
    def walk(node):
        stack = list()
        stack.append(node)
        while stack:
            node = stack.pop()
            if node.children: symbols[node.label] = symbols.get(node.label, 0) + 1
            for child in node.children:
                stack.append(child)
    
    for tree in trees:
        walk(tree)
    
    s = '\n'.join(
        ', '.join((name, str(count))) for name, count in symbols.iteritems()
    )

    f = open(fname, 'w')
    f.write(s)
    f.write('\n'*2)
    f.close()

