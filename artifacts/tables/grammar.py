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

@registration.register('table', depends=['verify_grammar'])
def grammar(path, oldtable, tables, conf):
    return conf['grammar']