#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, sys, traceback, subprocess, itertools, contextlib

import coverage
from ply import yacc
from lexer import tokens, Lexer
from ast import Node

## If you are confused about the syntax in this file I recommend reading the
## documentation on the PLY website to see how this compiler compiler's syntax
## works.
class Parser(object):

    tokens = tokens
    precedence = (
    )

    def __new__(cls, **kwargs):
        ## Does magic to allow PLY to do its thing.
        self = super(Parser, cls).__new__(cls, **kwargs)
        self.table = dict()
        self.loc = list()
        self.yacc = yacc.yacc(module=self,  tabmodule="parser_tab", debug=0, **kwargs)
        return self.yacc

    def p_Start(self, t):
        'Start : Stmts'

    def p_Stmts1(self, t):
        'Stmts : Stmts Stmt'

    def p_Stmts2(self, t):
        'Stmts : Stmt'

    def p_Stmt0(self, t):
        'Stmt : PRINT NAME'
        name = t[2]
        if name not in self.table:
            msg = '%s has not been declared' % name
            raise Exception, msg
        print self.table[name]

    def p_Stmt2(self, t):
        'Stmt : VAR NAME EQUAL INT_VAL'
        name = t[2]
        if name in self.table:
            raise Exception, '%s redeclared' % name
        self.table[name] = t[4]

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)

def read(path):
    f = open(path, 'r')
    s = f.read()
    f.close()
    return s

def parse(s):
    return Parser().parse(s, lexer=Lexer())

if __name__ == '__main__':
    parse(raw_input(''))

