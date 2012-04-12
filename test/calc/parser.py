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
        'Start : Expr'
        t[0] = self.__create(t)

    def p_Expr1(self, t):
        'Expr : Expr PLUS Term'
        t[0] = self.__create(t)

    def p_Expr2(self, t):
        'Expr : Expr DASH Term'
        t[0] = self.__create(t)

    def p_Expr3(self, t):
        'Expr : Term'
        t[0] = self.__create(t)

    def p_Term1(self, t):
        'Term : Term STAR Exp'
        t[0] = self.__create(t)

    def p_Term2(self, t):
        'Term : Term SLASH Exp'
        t[0] = self.__create(t)

    def p_Term3(self, t):
        'Term : Exp'
        t[0] = self.__create(t)

    def p_Exp1(self, t):
        'Exp : Exp EXP Unary'
        t[0] = self.__create(t)

    def p_Exp2(self, t):
        'Exp : Unary'
        t[0] = self.__create(t)

    def p_Unary1(self, t):
        'Unary : DASH PostUnary'
        t[0] = self.__create(t)

    def p_Unary2(self, t):
        'Unary : PostUnary'
        t[0] = self.__create(t)

    def p_PostUnary1(self, t):
        'PostUnary : Factor T'
        t[0] = self.__create(t)

    def p_PostUnary2(self, t):
        'PostUnary : Factor'
        t[0] = self.__create(t)

    def p_Factor1(self, t):
        'Factor : Value'
        t[0] = self.__create(t)

    def p_Factor2(self, t):
        'Factor : LPAREN Expr RPAREN'
        t[0] = self.__create(t)

    def p_Value1(self, t):
        'Value : Atom'
        t[0] = self.__create(t)

    def p_Value2(self, t):
        'Value : Log'
        t[0] = self.__create(t)

    def p_Value3(self, t):
        'Value : LSQUARE Matrix RSQUARE'
        t[0] = self.__create(t)

    def p_Value4(self, t):
        'Value : LANGLE Vector RANGLE'
        t[0] = self.__create(t)

    def p_Atom1(self, t):
        'Atom : NUMBER'
        t[0] = self.__create(t)

    def p_Log1(self, t):
        'Log : LOG LPAREN Expr COMMA Expr RPAREN'
        t[0] = self.__create(t)

    def p_Matrix1(self, t):
        'Matrix : Matrix SEMI Vector'
        t[0] = self.__create(t)

    def p_Matrix2(self, t):
        'Matrix : Vector'
        t[0] = self.__create(t)

    def p_Vector1(self, t):
        'Vector : Vector COMMA Expr'
        t[0] = self.__create(t)

    def p_Vector2(self, t):
        'Vector : Expr'
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
    trees = list()
    for path, text in files:
        print path, text
        trees.append((path, parse(text)))
    for path, tree in trees:
        f = open(path+'.ast', 'w')
        f.write(str(tree))
        f.close()

if __name__ == '__main__':
    main()

