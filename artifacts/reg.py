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

    def register(self, type, range=None):
        assert hasattr(self, 'basepath')
        assert type in self.types
        def default_range(conf):
            yield (conf,)
        if range is None: range = default_range
        def dec(f):
            name = f.func_name
            path = os.path.join(self.basepath, name)
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
            self._d.update({name:{'type':type, 'function':wrapper}})
            return wrapper
        return dec

    def __iter__(self):
        for key,val in self._d.iteritems(): yield key,val

registration = Registration()

