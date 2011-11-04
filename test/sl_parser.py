#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, sys, traceback, subprocess, itertools, contextlib

import coverage
from ply import yacc
from sl_lexer import tokens, Lexer
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
        'Stmt : PRINT Expr'
        t[0] = self.__create(t)

    def p_Stmt1(self, t):
        'Stmt : Call'
        t[0] = self.__create(t)

    def p_Stmt2(self, t):
        'Stmt : NAME EQUAL Expr'
        t[0] = self.__create(t)

    def p_Stmt3(self, t):
        'Stmt : NAME EQUAL FuncDecl'
        t[0] = self.__create(t)

    def p_Stmt4(self, t):
        'Stmt : IF LPAREN BooleanExpr RPAREN LCURLY Stmts RCURLY'
        t[0] = self.__create(t)

    def p_Stmt5(self, t):
        'Stmt : IF LPAREN BooleanExpr RPAREN LCURLY Stmts RCURLY ELSE LCURLY Stmts RCURLY'
        t[0] = self.__create(t)

    def p_Stmt6(self, t):
        'Stmt : VAR NAME'
        t[0] = self.__create(t)

    def p_Stmt7(self, t):
        'Stmt : VAR NAME EQUAL Expr'
        t[0] = self.__create(t)

    def p_Stmt8(self, t):
        'Stmt : VAR NAME EQUAL FuncDecl'
        t[0] = self.__create(t)

    def p_FuncDecl1(self, t):
        'FuncDecl : FUNC LPAREN RPAREN LCURLY Return RCURLY'
        t[0] = self.__create(t)

    def p_FuncDecl2(self, t):
        'FuncDecl : FUNC LPAREN RPAREN LCURLY Stmts Return RCURLY'
        t[0] = self.__create(t)

    def p_FuncDecl3(self, t):
        'FuncDecl : FUNC LPAREN DParams RPAREN LCURLY Return RCURLY'
        t[0] = self.__create(t)

    def p_FuncDecl4(self, t):
        'FuncDecl : FUNC LPAREN DParams RPAREN LCURLY Stmts Return RCURLY'
        t[0] = self.__create(t)

    def p_Return1(self, t):
        'Return : RETURN'
        t[0] = self.__create(t)

    def p_Return2(self, t):
        'Return : RETURN Expr'
        t[0] = self.__create(t)

    def p_Expr(self, t):
        'Expr : AddSub'
        t[0] = self.__create(t)

    def p_AddSub1(self, t):
        'AddSub : AddSub PLUS MulDiv'
        t[0] = self.__create(t)

    def p_AddSub2(self, t):
        'AddSub : AddSub DASH MulDiv'
        t[0] = self.__create(t)

    def p_AddSub3(self, t):
        'AddSub : MulDiv'
        t[0] = self.__create(t)

    def p_MulDiv1(self, t):
        'MulDiv : MulDiv STAR Atomic'
        t[0] = self.__create(t)

    def p_MulDiv2(self, t):
        'MulDiv : MulDiv SLASH Atomic'
        t[0] = self.__create(t)

    def p_MulDiv3(self, t):
        'MulDiv : Atomic'
        t[0] = self.__create(t)

    def p_Atomic1(self, t):
        'Atomic : Value'
        t[0] = self.__create(t)

    def p_Atomic2(self, t):
        'Atomic : LPAREN Expr RPAREN'
        t[0] = self.__create(t)

    def p_Value1(self, t):
        'Value : INT_VAL'
        t[0] = self.__create(t)

    def p_Value2(self, t):
        'Value : NAME'
        t[0] = self.__create(t)

    def p_Value3(self, t):
        'Value : Call'
        t[0] = self.__create(t)

    def p_Call1(self, t):
        'Call : NAME LPAREN Params RPAREN'
        t[0] = self.__create(t)

    def p_Call2(self, t):
        'Call : NAME LPAREN RPAREN'
        t[0] = self.__create(t)

    def p_Params1(self, t):
        'Params : Params COMMA Expr'
        t[0] = self.__create(t)

    def p_Params2(self, t):
        'Params : Expr'
        t[0] = self.__create(t)

    def p_DParams1(self, t):
        'DParams : DParams COMMA NAME'
        t[0] = self.__create(t)

    def p_DParams2(self, t):
        'DParams : NAME'
        t[0] = self.__create(t)

    def p_BooleanExpr(self, t):
        'BooleanExpr : OrExpr'
        t[0] = self.__create(t)

    def p_OrExpr1(self, t):
        'OrExpr : OrExpr OR AndExpr'
        t[0] = self.__create(t)

    def p_OrExpr2(self, t):
        'OrExpr : AndExpr'
        t[0] = self.__create(t)

    def p_AndExpr1(self, t):
        'AndExpr : AndExpr AND NotExpr'
        t[0] = self.__create(t)

    def p_AndExpr2(self, t):
        'AndExpr : NotExpr'
        t[0] = self.__create(t)

    def p_NotExpr1(self, t):
        'NotExpr : NOT BooleanTerm'
        t[0] = self.__create(t)

    def p_NotExpr2(self, t):
        'NotExpr : BooleanTerm'
        t[0] = self.__create(t)

    def p_BooleanTerm1(self, t):
        'BooleanTerm : CmpExpr'
        t[0] = self.__create(t)

    def p_BooleanTerm5(self, t):
        'BooleanTerm : LPAREN BooleanExpr RPAREN'
        t[0] = self.__create(t)

    def p_CmpExpr(self, t):
        'CmpExpr : Expr CmpOp Expr'
        t[0] = self.__create(t)

    def p_CmpOp(self, t):
        '''CmpOp : EQEQ
                | NQ
                | LT
                | LE
                | GT
                | GE'''
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

if __name__ == '__main__':
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
