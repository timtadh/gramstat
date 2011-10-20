#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, sys, functools

class Registration(object):

    types = ['img', 'table']

    def __init__(self):
        self._d = dict()
        self.tables = dict()

    def init(self, conf):
        self.basepath = conf['outdir']
        self.loadtables = conf['loadtables']
        self.loadpath = conf['loadpath']
        self.requested = conf['requested_artifacts']

    def _loadtable(self, name, path, rowloader):
        if not (os.path.exists(path) and os.path.isfile(path)): return
        f = open(path, 'r')
        s = f.read()
        f.close()

        table = tuple(
            rowloader(row)
            for row in s.split('\n') if row
        )
        self.tables[name] = table

    def register(self, type, range=None, rowloader=None, depends=None):
        assert hasattr(self, 'basepath')
        assert type in self.types
        def default_range(conf):
            yield (conf,)
        def default_rowloader(row):
            return tuple(col.strip() for col in row.split(','))
        if range is None: range = default_range
        if rowloader is None: rowloader = default_rowloader
        if depends is None: depends = list()

        def dec(f):
            name = f.func_name

            path = os.path.join(self.basepath, name)
            path += '' if type == 'img' else '.csv'
            if name in self.requested:
                path = self.requested[name]
            if type == 'table' and self.loadtables:
                loadpath = os.path.join(self.loadpath, name) + '.csv'
                self._loadtable(name, loadpath, rowloader)

            @functools.wraps(f)
            def wrapper(conf):
                for obj in range(conf):
                    if type == 'img':
                        f(path, self.tables, *obj)
                    elif type == 'table':
                        if name not in self.tables:
                            self.tables[name] = None
                        self.tables[name] = f(path, self.tables[name], *obj)
                    else:
                        raise Exception, 'Should be unreachable.'
            self._d.update({
                    name: {
                        'name':name,
                        'type':type,
                        'function':wrapper,
                        'depends':depends,
                    }})
            return wrapper

        return dec

    def __iter__(self):

        ## This computes a topological sort of the dependency graph so we can
        ## visit the functions in the correct order.
        visited = set()
        order = list()
        def visit(n):
            if n['name'] not in visited:
                visited.add(n['name'])
                for m in n['depends']:
                    if m not in self._d:
                        raise Exception, (
                            "Could not find dependency '%s' of artifact '%s'"
                        ) % (m, n['name'])
                    visit(self._d[m])
                order.append(n)

        for n in self._d.itervalues():
            visit(n)

        for n in order: yield n['name'], n

registration = Registration()

