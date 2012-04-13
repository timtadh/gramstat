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

    counts = dict() #counts how many times a RULE is reached by a specific prevTuple (e.g. counts[NT => A:B:C][(NT1,NT2)] == 5)
    terminalCounts = dict() #counts how many times a prevTuple reaches a specific NONTERMINAL (e.g. terminalCounts[(NT1,NT2)][NT] == 78)
    stack = list()
    lookBack = 2 #how many items in prevTuple?
    def callback(grammar, node, depth):
        #if this is a new ast then we want to clear our stack
        if node.label == "Start":
            while stack:
                stack.pop()
            initStack = (tuple(None for x in range(lookBack)), False)
            stack.append(initStack)

        prev = stack[len(stack)-1][0]
        requirePop = stack[len(stack)-1][1]

        prevAsTuple = tuple(prev[x] for x in range(lookBack))

        if not node.children:
            if requirePop:
                stack.pop()
            return

        if requirePop:
            stack.pop()

        productions = grammar[node.label]
        p = productions.index(':'.join(kid.label for kid in node.children)) + 1

        chosenRule = node.label + " => " + grammar[node.label][p-1]


        if not counts.has_key(chosenRule):
            counts[chosenRule] = {prevAsTuple : 1}
        else:
            if not counts.get(chosenRule).has_key(prevAsTuple):
                counts[chosenRule][prevAsTuple] = 1
            else:
                counts[chosenRule][prevAsTuple] += 1

        if not terminalCounts.has_key(prevAsTuple):
            terminalCounts[prevAsTuple] = {node.label : 1}
        else:
            if not terminalCounts.get(prevAsTuple).has_key(node.label):
                terminalCounts[prevAsTuple][node.label] = 1
            else:
                terminalCounts[prevAsTuple][node.label] += 1

        #append this new rule to the stack as our new "most previous"
        if grammar[node.label][p-1].count(":") > 1:
            stack.append(
                (
                    tuple(prev[x+1] for x in range(lookBack-1)) + (node.label,),
                    False
                )
            )
        else: #if there is only one nonterminal in this rule then we want to log it as a previous but then pop it from the stack
              #this way, rules that have >1 nonterminals will keep their "prev" relative to what it was originally.
              #e.g. with NT:NT2:NT3, when we get to NT2, we dont want previous to include the previous from when we went down NT's productions
            stack.append(
                (
                    tuple(prev[x+1] for x in range(lookBack-1)) + (node.label,),
                    True
                 )
            )
    walktrees(conf['trees'], functools.partial(callback, grammar))


    probabilities = dict(
        (
          rule,
          dict(
            (
              prev,
              float(num)/float(terminalCounts[prev][rule.split("=>")[0].strip()]) #P[rule | prev]
            )
            for prev, num in myCounts.iteritems()
          )
        )
        for rule, myCounts in counts.iteritems()
    )

    table = tuple(
        (lookBack, prod) + tuple(nt for nt in prev) + (probability,)
        for prod, myCounts in probabilities.iteritems()
            for prev, probability in myCounts.iteritems()
    )

    save(path, table)
    return table