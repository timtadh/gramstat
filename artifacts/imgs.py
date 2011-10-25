#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess, math
from decimal import Decimal as dec

import reg
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab



def dot(name, dotty):
    dot = name + '.dot'
    plain = name + '.plain'
    png = name + '.png'

    f = open(dot, 'w')
    f.write(dotty)
    f.close()

    p = subprocess.Popen(['dot', '-Tplain', '-o', plain], stdin=subprocess.PIPE)
    p.stdin.write(dotty + '\0')
    p.stdin.close()
    p.wait()

    p = subprocess.Popen(['dot', '-Tpng', '-o', png], stdin=subprocess.PIPE)
    p.stdin.write(dotty + '\0')
    p.stdin.close()
    p.wait()

def trees(conf):
    for i, tree in enumerate(conf['trees']):
        yield i, tree

@reg.registration.register('img', range=trees)
def ast_imgs(outdir, tables, i, tree):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    dot(os.path.join(outdir, str(i)), tree.dotty())

def create_histogram(title, path, table, height=1, shape=None):
    if shape is None: shape = [0.05, .1, 0.90, 0.8]
    fname = path + '.png'
    table = list(table)
    table.sort(key=lambda x: x[1])
    table.reverse()
    y = np.array([count for name, count in table])
    #y = y

    fig = plt.figure()
    ax = fig.add_axes(shape)

    x = [i for i in xrange(0, len(y))]
    rects1 = ax.bar(x, y, color='r')

    ax.set_xlabel('Symbols')
    ax.set_ylabel('Number of Appearances')
    labels = tuple(name for name, count in table)
    ax.set_xlim(0, len(x))
    ax.set_xticklabels(labels, clip_on=False)
    xaxis = ax.get_xaxis()
    xaxis.set_ticks([i+.4 for i in xrange(0, len(y))])
    xaxis.set_ticklabels(labels)

    fig.suptitle(title)
    fig.set_size_inches(int(len(y)*1.2 + .5), 10*height)
    fig.savefig(fname, format='png')


@reg.registration.register('img', depends=['symbol_count'])
def symbol_histogram(path, tables, conf):
    create_histogram('All Symbols', path, tables['symbol_count'])

@reg.registration.register('img', depends=['term_count'])
def term_histogram(path, tables, conf):
    create_histogram('Terminal Symbols', path, tables['term_count'])

@reg.registration.register('img', depends=['non_term_count'])
def nonterm_histogram(path, tables, conf):
    create_histogram('Non-Terminal Symbols', path, tables['non_term_count'])

@reg.registration.register('img', depends=['production_count'])
def production_histogram(path, tables, conf):
    table = [
        (nonterm + ' =\n' + '\n'.join(c for c in p.split(':')), int(count))
        for nonterm, p, count in tables['production_count']
    ]
    create_histogram('Productions', path, table, 2, [0.05, .2, 0.90, 0.7])

@reg.registration.register('img', depends=['tree_number'])
def normal_probability_plot(path, tables, conf):
    fname = path + '.png'
    treenums = tables['tree_number']
    x = sorted([float(dec(num).log10().log10()) for ast, num in treenums])
    y = [100.0*((j - 0.5)/float(len(x))) for j in xrange(1, len(x)+1)]

    coefficients = np.polyfit(x, y, 1)
    polynomial = np.poly1d(coefficients)
    ys = polynomial(x)

    fig = plt.figure()
    #fig.ylim(0, 100)
    #print dir(fig)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    print stats.probplot(x, dist='norm', plot=plt)
    ##ax.plot(x, y, 'o')
    #ax.plot(x, ys)
    #ax.xaxis.set_label_text('x(j)')
    #ax.yaxis.set_label_text('100*(j - .5)/N')
    #print dir(ax.yaxis)
    #ax.yaxis.limit_range_for_scale(0, 100)
    #ax.xlim(174,222)
    #ax.set_ylim(0,100)
    #ax.ylabel('y')
    #ax.xlabel('x')
    #ax.set_yscale('log')
    plt.savefig(fname, format='png')
    for i in x:
        print i
