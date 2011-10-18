#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, os, subprocess

import reg

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
def ast_imgs(outdir, i, tree):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    dot(os.path.join(outdir, str(i)), tree.dotty())


