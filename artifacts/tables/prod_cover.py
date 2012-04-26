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


def callback(grammar, cov, node, depth):
    if not node.children: return
    productions = grammar[node.label]
    p = productions.index(':'.join(kid.label for kid in node.children)) + 1
    cov[(node.label, p)] = 1

#@registration.register('table', depends=['grammar'])
def production_coverage_local(path, oldtable, tables, conf):
    grammar = dict(
      (
        nonterm,
        tuple(sorted(':'.join(p) for p in prods))
      )
      for nonterm, prods in conf['grammar'].iteritems()
    )
    def initstats():
        stats = dict()
        total = 0
        for nonterm, P in grammar.iteritems():
            for i, p in enumerate(P):
                stats[(nonterm, i+1)] = 0
                total += 1
        return stats, total

    for tree in conf['trees']:
        local_cov, total = initstats()
        walktree(tree, functools.partial(callback, grammar, local_cov))
        print float(sum(val for val in local_cov.itervalues()))/total

#@registration.register('table', depends=['grammar'])
def production_coverage_global(path, oldtable, tables, conf):
    grammar = dict(
      (
        nonterm,
        tuple(sorted(':'.join(p) for p in prods))
      )
      for nonterm, prods in conf['grammar'].iteritems()
    )
    def initstats():
        stats = dict()
        total = 0
        for nonterm, P in grammar.iteritems():
            for i, p in enumerate(P):
                stats[(nonterm, i+1)] = 0
                total += 1
        return stats, total


    global_cov, total = initstats()
    walktrees(conf['trees'], functools.partial(callback, grammar, global_cov))
    print 'global', float(sum(val for val in global_cov.itervalues()))/total
