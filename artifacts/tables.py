#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess, functools, collections

from reg import registration
import sieve, lib

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
    def callback(symbols, node, depth):
        symbols[node.label] = symbols.get(node.label, 0) + 1
    return symbol_counter(path, oldtable, conf['trees'], callback)

@registration.register('table', rowloader=symcount_rowloader)
def non_term_count(path, oldtable, tables, conf):
    def callback(symbols, node, depth):
        if node.children: symbols[node.label] = symbols.get(node.label, 0) + 1
    return symbol_counter(path, oldtable, conf['trees'], callback)

@registration.register('table', rowloader=symcount_rowloader)
def term_count(path, oldtable, tables, conf):
    def callback(symbols, node, depth):
        if not node.children: symbols[node.label] = symbols.get(node.label, 0) + 1
    return symbol_counter(path, oldtable, conf['trees'], callback)

@registration.register('table', ext='.grammar')
def infer_grammar(path, oldtable, tables, conf):
    productions = dict()
    if oldtable is not None:
        ## TODO: clean this jankyness up! we shouldn't have to rejoin oldtable
        ## so we can parse it.
        productions.update(
          lib.parse_grammar('\n'.join(''.join(row) for row in oldtable))
        )

    def callback(productions, node, depth):
        if not node.children: return
        p = productions.get(node.label, set())
        p.add(tuple(kid.label for kid in node.children))
        productions[node.label] = p
    walktrees(conf['trees'], functools.partial(callback, productions))

    table = tuple(
        tuple([nonterm] + [':'.join(p) for p in P])
        for nonterm, P in productions.iteritems()
    )
    gramfile = '\n'.join(
        ' : '.join((
            nonterm,
            ' '.join(prod)
        ))
        for nonterm, prods in productions.iteritems()
        for prod in prods
    ) + '\n'
    with open(path, 'w') as f: f.write(gramfile)
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

    def callback(grammar, stats, node, depth):
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

@registration.register('table', depends=['production_count', 'infer_grammar'])
def production_probability(path, oldtable, tables, conf):
    grammar = dict((row[0], tuple(row[1:])) for row in tables['infer_grammar'])
    pcount = tuple(tables['production_count'])
    collect = dict()

    prodnum = dict()
    for nonterm, P in grammar.iteritems():
        for i, p in enumerate(P):
            prodnum[(nonterm, p)] = i+1

    for nonterm, p, count in pcount:
        prods = collect.get(nonterm, dict())
        prods[p] = count
        collect[nonterm] = prods

    probabilities = dict(
        (
          nonterm,
          dict(
            (
              name,
              float(count)/float(sum(count for count in prods.itervalues()))
            )
            for name, count in prods.iteritems()
          )
        )
        for nonterm, prods in collect.iteritems()
    )

    table = tuple(
        (nonterm, production, probability)
        for nonterm, prods in probabilities.iteritems()
            for production, probability in prods.iteritems()
    )

    save(path, table)
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

@registration.register('table', uses=['grammar'], depends=['infer_grammar'])
def verify_grammar(path, oldtable, tables, conf):
    igram = dict(
      (
        row[0],
        set(tuple(prod.split(':')) for prod in row[1:])
      )
      for row in tables['infer_grammar']
    )
    kgram = conf['grammar']
    def check(X, Y, x_name, y_name):
        for nonterm, x_prods in X.iteritems():
            if nonterm not in Y:
                print >>sys.stderr, (
                  'WARNING: nonterm "%s" not found in "%s"'
                ) % (nonterm, y_name)
                continue
            y_prods = Y[nonterm]
            X_tra = x_prods - y_prods
            if X_tra:
                print >>sys.stderr, (
                  'WARNING: productions where found in "%s" but not in "%s"\n'
                  '     %s -> %s'
                ) % (
                  x_name, y_name, nonterm,
                  '\n           | '.join(' '.join(p) for p in X_tra)
                )

    check(igram, kgram, 'inferred grammar', 'supplied grammar')

@registration.register('table', uses=['grammar'], depends=['verify_grammar'])
def grammar(path, oldtable, tables, conf):
    return conf['grammar']
