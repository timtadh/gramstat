#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from reg import registration

INITED = False
def defered_imports(conf):
    global INITED
    if INITED: return
    INITED = True
    registration.init(conf)
    import imgs
    import tables

def produce(conf):
    '''Create the artifacts requested by the configuration using the various
    options indicated.
    '''
    defered_imports(conf)
    for name, f in filter_artifacts(conf, available_artifacts(conf)):
        f(conf)

def available_artifacts(conf):
    '''Create a dictionary of all of the available artifacts that /could/ be
    created.
    @params conf : The configuration created by stat.py
    @returns : map string -> {'function':f, 'type':type}
    '''
    defered_imports(conf)
    return tuple((name, d)
      for name, d in registration)

class filter_artifacts(object):

    cache = None

    def __new__(cls, conf, artifacts):
        '''Filter the list of artifacts via the specified configuration.
        @params conf : The configuration created by stat.py
        @params artifacts : map string -> {'function':f, 'type':type}
        @returns : a new map string -> function
        '''
        if cls.cache is not None: return cls.cache

        def _reached_by():
            visited = set()
            depended_on_by = dict((name, list()) for name, n in artifacts)
            reached_by = dict((name, list()) for name, n in artifacts)

            for name, n in artifacts:
                for child in n['depends']:
                    depended_on_by[child].append(name)
                    reached_by[child].append(name)

            def visit(name):
                if name not in visited:
                    visited.add(name)
                    for child in depended_on_by[name]:
                        reached_by[name] += visit(child)
                return reached_by[name]

            for name, n in artifacts:
                visit(name)

            return reached_by

        reached_by = _reached_by()

        def accept(d):
            if d['name'] in conf['requested_artifacts']: return True
            elif d['type'] == 'img' and conf['genimgs']: return True
            elif d['type'] == 'table' and conf['gentables']: return True
            return False

        def dependency(name, required):
            for req in required:
                if req in reached_by[name]:
                    return True
            return False

        required = set(name for name, d in artifacts if accept(d))
        cls.cache = tuple((name, d['function'])
            for name, d in artifacts if accept(d) or dependency(name, required))
        return cls.cache



