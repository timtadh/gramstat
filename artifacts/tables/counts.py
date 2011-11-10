#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess, functools, collections

from artifacts.reg import registration
from artifacts import sieve
import lib

from generic import walktree, walktrees, save

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

