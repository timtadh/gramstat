#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

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
            '''Computes the inverse transitive closure of the dependency graph
            so we can check if a particular artifact is being depended on by a
            required artifact.
            '''
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

        def isrequired(d):
            '''Is this a required object?'''
            for use in d['uses']:
                if not conf[use]: return False
            if d['name'] in conf['excluded_artifacts']: return False
            elif d['name'] in conf['requested_artifacts']: return True
            elif d['type'] == 'img' and conf['genimgs']: return True
            elif d['type'] == 'table' and conf['gentables']: return True
            return False

        def allow(d):
            for use in d['uses']:
                if conf[use]: continue
                if conf['list_artifacts']:
                    sys.stderr.write('WARNING: ')
                sys.stderr.write((
                    'Artifact "%s" was requested but requires "%s" which was '
                    'not supplied.\n\n'
                ) % (d['name'], use))
                if not conf['list_artifacts']:
                    sys.exit(99)
                else:
                    return False
            return True

        def isdependency(name, d, required):
            '''Do any of the required artifacts depend on this one?'''
            for req in required:
                if req in reached_by[name]:
                    return True
            return False

        reached_by = _reached_by()
        required = set(name for name, d in artifacts if isrequired(d))
        cls.cache = tuple(
            (name, d['function'])
            for name, d in artifacts
            if allow(d) and (isrequired(d) or isdependency(name, d, required))
        )

        return cls.cache



