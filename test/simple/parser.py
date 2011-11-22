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


def get(self, n):
    if n >= 0: return self.slice[n]
    else: return self.stack[n].value

setattr(yacc.YaccProduction, 'get', get)



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
        self.yacc = yacc.yacc(module=self,  tabmodule="sl_parser_tab", debug=0, **kwargs)
        return self.yacc

    def __create(self, t):
        #print type(t), help(t)

        doc = self.__getattribute__(traceback.extract_stack()[-2][2]).__doc__
        name = doc.split(':', 1)[0].strip()
        node = Node(name)
        for i, x in enumerate(t[1:]):
            if isinstance(x, Node):
                node.addkid(x)
            else:
                tok = t.get(i+1)
                node.addkid(Node(tok.type + ':' + str(tok.value)))
        return node

    def p_Start(self, t):
        'Start : Stmts'
        t[0] = self.__create(t)

    def p_Stmts1(self, t):
        'Stmts : Stmts Stmt'
        t[0] = self.__create(t)

    def p_Stmts2(self, t):
        'Stmts : Stmt'
        t[0] = self.__create(t)

    def p_Stmt0(self, t):
        'Stmt : PRINT NAME'
        t[0] = self.__create(t)

    def p_Stmt2(self, t):
        'Stmt : VAR NAME EQUAL INT_VAL'
        t[0] = self.__create(t)

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)

def read(path):
    f = open(path, 'r')
    s = f.read()
    f.close()
    return s

def parse(s):
    return Parser().parse(s, lexer=Lexer())

def main():
    if not sys.argv[1:]: sys.exit(1)
    file_names = [os.path.abspath(s) for s in sys.argv[1:]]
    files = [(path, read(path)) for path in file_names]
    trees = [(path, parse(text)) for path, text in files]
    for path, tree in trees:
        f = open(path+'.ast', 'w')
        f.write(str(tree))
        f.close()


if __name__ == '__main__':
    main()

