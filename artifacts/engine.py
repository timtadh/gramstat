#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from reg import registration
import imgs
import tables

def produce(conf):
    '''Create the artifacts requested by the configuration using the various
    options indicated.
    '''
    for f in filter_artifacts(conf, available_artifacts(conf)).itervalues():
        f(conf)

def available_artifacts(conf):
    '''Create a dictionary of all of the available artifacts that /could/ be
    created. 
    @params conf : The configuration created by stat.py
    @returns : map string -> {'function':f, 'type':type}
    '''
    return dict((name, d)
      for name, d in registration)

def filter_artifacts(conf, artifacts):
    '''Filter the list of artifacts via the specified configuration.
    @params conf : The configuration created by stat.py
    @params artifacts : map string -> {'function':f, 'type':type}
    @returns : a new map string -> function
    '''
    def accept(name, d):
        if name in conf['requested_artifacts']: return True
        elif d['type'] == 'img' and conf['genimgs']: return True
        elif d['type'] == 'table' and conf['gentables']: return True
        return False

    return dict((name, d['function']) 
        for name, d in artifacts.iteritems() if accept(name, d))


