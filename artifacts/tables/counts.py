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
    #print grammar
    #print "\n"
    for nonterm, P in grammar.iteritems():
        for i, p in enumerate(P):
            prodnum[(nonterm, p)] = i+1
            stats[(nonterm, i+1)] = 0
    if oldtable is not None:
        for nonterm, p, count in oldtable:
            stats[(nonterm, prodnum[(nonterm, p)])] = int(count)
    #print prodnum
    def callback(grammar, stats, node, depth):
        if not node.children: return
        productions = grammar[node.label]
        p = productions.index(':'.join(kid.label for kid in node.children)) + 1
        #print node.label + " => " + grammar[node.label][p-1]
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
    #print "\n"
    #print pcount
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

@registration.register('table', depends=['production_count', 'infer_grammar'])
def conditional_probabilities(path, oldtable, tables, conf):
    grammar = dict((row[0], tuple(row[1:])) for row in tables['infer_grammar'])
    stats = dict()
    prodnum = dict()
    #print grammar
    #print "\n"
    for nonterm, P in grammar.iteritems():
        for i, p in enumerate(P):
            prodnum[(nonterm, p)] = i+1
            stats[(nonterm, i+1)] = 0
    if oldtable is not None:
        for nonterm, p, count in oldtable:
            stats[(nonterm, prodnum[(nonterm, p)])] = int(count)
    #print prodnum


    counts = dict()
    stack = list()
    def callback(grammar, stats, node, depth):
        if node.label == "Start":
            while stack:
                stack.pop()
            counts.clear()
            prev2 = (None, None, False)
            stack.append(prev2)

        if not node.children:
            if stack[len(stack)-1][2]:
                stack.pop()
            return
        prev2 = stack[len(stack)-1]
        if prev2[2]:
            stack.pop()
        productions = grammar[node.label]
        p = productions.index(':'.join(kid.label for kid in node.children)) + 1


        if not counts.has_key(node.label):
            counts[node.label] = {(prev2[0], prev2[1]) : 1}
        else:
            if not counts.get(node.label).has_key((prev2[0], prev2[1])):
                counts[node.label][(prev2[0], prev2[1])] = 1
            else:
                 counts[node.label][(prev2[0], prev2[1])] += 1


        if grammar[node.label][p-1].count(":") > 1:
            stack.append((prev2[1], grammar[node.label][p-1], False))
        else:
            stack.append((prev2[1], grammar[node.label][p-1], True))
        stats[(node.label, p)] += 1
    walktrees(conf['trees'], functools.partial(callback, grammar, stats))


    #now we normalize
    probabilities = dict(
        (
          nonterm,
          dict(
            (
              prev2,
              float(num)/float(sum(num for num in myCounts.itervalues()))
            )
            for prev2, num in myCounts.iteritems()
          )
        )
        for nonterm, myCounts in counts.iteritems()
    )

    table = tuple(
        (nonterm, prev2, probability)
        for nonterm, myCounts in probabilities.iteritems()
            for prev2, probability in myCounts.iteritems()
    )

    save(path, table)
    return table
