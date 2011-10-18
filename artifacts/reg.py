#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools

class Registration(object):

    types = ['img', 'table']
    
    def __init__(self):
        self._d = dict()

    def register(self, name, type):
        assert type in self.types
        def dec(f):
            self._d.update({name:{'type':type, 'function':f}})
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapper
        return dec

    def __iter__(self):
        for key,val in self._d.iteritems(): yield key,val

registration = Registration()

