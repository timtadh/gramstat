#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess, functools

from reg import registration
import sieve

def walktree(root, process):
    stack = list()
    stack.append(root)
    while stack:
        node = stack.pop()
        process(node)
        for child in node.children:
            stack.append(child)

def walktrees(trees, process):
    for tree in trees:
        walk(tree, process)

def save(path, table):
    s = '\n'.join( ', '.join(str(col) for col in row) for row in table )
    f = open(path, 'w')
    f.write(s)
    f.write('\n'*2)
    f.close()
    return table

def symbol_counter(path, oldtable, trees, callback):
    symbols = dict()
    if oldtable is not None:
        symbols.update(oldtable)
    walktrees(trees, functools.partial(callback, symbols))

    return save(path, tuple((name,count)
        for name, count in symbols.iteritems()))

def symcount_rowloader(row):
    name, count = row.split(',')
    return (name, int(count))

@registration.register('table', rowloader=symcount_rowloader)
def symbol_count(path, oldtable, tables, conf):
    def callback(symbols, node):
        symbols[node.label] = symbols.get(node.label, 0) + 1
    return symbol_counter(path, oldtable, conf['trees'], callback)

@registration.register('table', rowloader=symcount_rowloader)
def non_term_count(path, oldtable, tables, conf):
    def callback(symbols, node):
        if node.children: symbols[node.label] = symbols.get(node.label, 0) + 1
    return symbol_counter(path, oldtable, conf['trees'], callback)

@registration.register('table', rowloader=symcount_rowloader)
def term_count(path, oldtable, tables, conf):
    def callback(symbols, node):
        if not node.children: symbols[node.label] = symbols.get(node.label, 0) + 1
    return symbol_counter(path, oldtable, conf['trees'], callback)

@registration.register('table')
def infer_grammar(path, oldtable, tables, conf):
    productions = dict()
    if oldtable is not None:
        productions.update(
            (row[0], set(tuple(e for e in col.split(':')) for col in row[1:]))
                for row in oldtable
        )

    def callback(productions, node):
        if not node.children: return
        p = productions.get(node.label, set())
        p.add(tuple(kid.label for kid in node.children))
        productions[node.label] = p
    walktrees(conf['trees'], functools.partial(callback, productions))

    table = tuple(
        tuple([nonterm] + [':'.join(p) for p in P])
        for nonterm, P in productions.iteritems()
    )
    save(path, table)
    return table

@registration.register('table', depends=['infer_grammar'])
def production_count(path, oldtable, tables, conf):
    grammar = dict((row[0], tuple(row[1:])) for row in tables['infer_grammar'])
    stats = dict()
    prodnum = dict()
    for nonterm, P in grammar.iteritems():
        for i, p in enumerate(P):
            prodnum[(nonterm, p)] = i+1
            stats[(nonterm, i+1)] = 0
    if oldtable is not None:
        for nonterm, p, count in oldtable:
            stats[(nonterm, prodnum[(nonterm, p)])] = int(count)

    def callback(grammar, stats, node):
        if not node.children: return
        productions = grammar[node.label]
        p = productions.index(':'.join(kid.label for kid in node.children)) + 1
        stats[(node.label, p)] += 1
    walktrees(conf['trees'], functools.partial(callback, grammar, stats))

    table = [
        (key[0], grammar[key[0]][key[1]-1], count)
        for key, count in stats.iteritems()
    ]
    table.sort(key=lambda x: (x[0], x[2]))
    save(path, table)
    return table

@registration.register('table')
def tree_number(path, oldtable, tables, conf):

    class callback(object):

        def __init__(self):
            self.acc = 1
            self.primes = sieve.find_primes()

        def __call__(self, node):
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
