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
                node.addkid(t.get(i+1).type)
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
    if not sys.argv[2:]: sys.exit(1)
    slang_loc = sys.argv[1]
    file_names = [os.path.abspath(s) for s in sys.argv[2:]]
    files = [(path, read(path)) for path in file_names]
    trees = [(path, parse(text)) for path, text in files]
    for path, tree in trees:
        f = open(path+'.ast', 'w')
        f.write(str(tree))
        f.close()

    @contextlib.contextmanager
    def eraser():
        erase = subprocess.Popen(['coverage', 'erase'])
        erase.wait()
        yield
        erase = subprocess.Popen(['coverage', 'erase'])
        erase.wait()


    for fname, text in files:
        with eraser():
            slang = subprocess.Popen(
                  [
                    'coverage', 'run',
                    os.path.join(slang_loc, 'slang'), '--stdin'
                  ],
                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE
            )
            slang.communicate(text)
            os.unlink('a.out')
            os.unlink('a.out.o')

            cov = coverage.coverage()
            cov.load()
            find = subprocess.Popen(
                ['find', slang_loc, '-name', '*.py'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE
            )
            grep = subprocess.Popen(
                ['grep', '-v', '/t_[^/]*'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE
            )
            slang_files = [f
              for f in grep.communicate(find.communicate('')[0])[0].split('\n')
              if f
            ]

            table = [[os.path.relpath(name, slang_loc)] + \
                [len(cov.analysis(name)[1])] + \
                sorted(
                  list(set(cov.analysis(name)[1]) - set(cov.analysis(name)[2]))
                )
              for name in slang_files
            ]
            s = '\n'.join(', '.join(str(col) for col in row) for row in table)
            f = open(fname+'.coverage', 'w')
            f.write(s)
            f.close()

if __name__ == '__main__':
    print parse('var x = 10 print x')

