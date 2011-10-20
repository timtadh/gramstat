#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess

import reg
import numpy as np
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


@reg.registration.register('img', depends=['symbol_count'])
def symbol_histogram(path, tables, conf):
    fname = path + '.png'
    symbol_count = list(tables['symbol_count'])
    symbol_count.sort(key=lambda x: x[1])
    symbol_count.reverse()
    y = np.array([count for name, count in symbol_count])
    #y = y

    fig = plt.figure()
    ax = fig.add_axes([0.05, .1, 0.90, 0.8])

    x = [i for i in xrange(0, len(y))]
    rects1 = ax.bar(x, y, color='r')

    ax.set_xlabel('Symbols')
    ax.set_ylabel('Number of Appearances')
    labels = tuple(name for name, count in symbol_count)
    ax.set_xlim(0, len(x))
    ax.set_xticklabels(labels, clip_on=False)
    xaxis = ax.get_xaxis()
    xaxis.set_ticks([i+.4 for i in xrange(0, len(y))])
    xaxis.set_ticklabels(labels)

    fig.set_size_inches(int(len(y)*.75 + .5), 10)
    fig.savefig(fname, format='png')
    return None
