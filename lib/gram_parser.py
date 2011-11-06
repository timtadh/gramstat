#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

def parse_grammar(s):
    grammar = dict()
    for row in s.split('\n'):
        if not row: continue
        nonterm, prod = row.split(':', 1)
        nonterm = nonterm.strip()
        prods = grammar.get(nonterm, set())
        prods.add(tuple(p.strip() for p in prod.split()))
        grammar[nonterm] = prods
    return grammar
