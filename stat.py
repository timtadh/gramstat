#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, sys
from getopt import getopt, GetoptError

import ast, artifacts, lib

VERSION = 'git master'

error_codes = {
    'usage':1,
    'file_not_found':2,
    'option':3,
    'args':4,
    'version':5,
    'bad_bool':6,
    'no_args':7,
    'bad_artspec':8,
    'bad_file_reads':9,
    'stdin_and_files':10,
    'file_instead_of_dir':11,
    'stdin_and_coverage':12,
}

usage_message = \
'''usage: stat.py [Options] [FILE]+'''

extended_message = \
'''
Explanation

    Generates statistics on parse trees. "[FILE]+" is a list of files containing
    serialized parse trees. The format for the parse tree is a pre-order
    enumeration.

      grammar

        nodes := nodes node
        nodes := node
        node := NUM COLON STRING NEWLINE

        COLON = r':'
        NUM = r'[0-9]+'
        STRING = r'.+$'
        NEWLINE = "\\n"

        NB: Whitespace is signficant, but STRING matches whitespace (except for
            newline).

      eg.

        2:root
        2:left side
        0:x
        1:y
        0:z
        3:right side
        0:a
        0:b
        0:c

      corresponds to
                              root
                              /  \
                             /    \
                    left side      right side
                    /    \         /    |    \
                   x      y       a     b     c
                          |
                          z

    Coverage [the -c or --coverage] option allow the user to supply coverage
    information in addition to the AST. The coverage information is statement
    level coverage of the result of the input being run through its intended
    program. By default the program looks for files which end in
    '$FILE.coverage', where $FILE is the associated AST. eg.

        If the program is run with

            ./stat.py -c `find test/ex -name '*.ast'`

        It would look for

            $ find test/ex/ -name "*.ast" | sed 's/\.ast/.coverage/'
            test/ex/29.sl.coverage
            test/ex/22.sl.coverage
            test/ex/10.sl.coverage
            test/ex/5.sl.coverage
            test/ex/28.sl.coverage
            test/ex/1.sl.coverage
            ...

    The coverage files are in CSV format

        file_name, number_executable_lines, executed, lines, enumerated, ...

Options

    -h, help                            print this message
    -v, version                         print the version
    -g, grammar=<file>                  supply a known grammar to annotate
    -o, outdir=<directory>              supply a path to a non-existant
                                          directory
                                          [default: ./gramstats]
    -i, imgs=<bool>                     generate images
                                          [default: true]
    -t, tables=<bool>                   generate statistic tables (as csv files)
                                          [default: true]
    -a, artifacts                       list what artifacts `stat.py` can
                                          generate
    -A, artifact=<artspec>              generate a specific artifact only.
                                          Multiple '-A' flags allowed.
                                          [overrides -o,-i, and -t]
    -E, exclude=<artifact>              exclude an artifact. This has no effect
                                          if another artifact (which is set to
                                          be generated depends on this artifact)
    -c, --coverage                      look for ".coverage" files (see
                                          explanation section for details) to
                                          supply coverage information for each
                                          AST.
    -T, usetables=<directory>           look for pre-existing statistic tables
                                          in this directory. With this option
                                          no other files are required, however
                                          if more examples are given the tables
                                          are updated. The new tables will only
                                          overwrite the old tables if
                                          "-o <dirname>" == "-T <dirname>"
    -s, stdin                           accept ASTs on standard in. With blank
                                          lines seperating trees. If files are
                                          supplied with this flag it will be an
                                          error. Unfortunately you cannot
                                          provide coverage information in this
                                          mode.

Specs

    <file>                              the path to a file
    <directory>                         the path to a directory.
    <bool>                              either "true" or "false"
    <artspec>                           <artifact>:<file>
                                        or <artifact> (default loc will be used)
    <artifact>                          an artifact in the list generated by
                                          --artifacts

'''


def log(msg):
    print msg

def version():
    '''Print version and exits'''
    log('stat.py version ' + VERSION)
    sys.exit(error_codes['version'])

def usage(code=None):
    '''Prints the usage and exits with an error code specified by code. If code
    is not given it exits with error_codes['usage']'''
    log(usage_message)
    if code is None:
        log(extended_message)
        code = error_codes['usage']
    sys.exit(code)

def mktree(s):
    '''Makes a tree from the pre-order enumeration. See the usage for the grammar.
    @params s : string in pre-order enumeration
    @returns <ast.Node> as the root of the tree.
    '''
    def g(s):
        for line in s.split('\n'):
            if not line: continue
            if ':' not in line:
                raise SyntaxError, 'Expected colon, none found.'
            children, sym = line.split(':', 1)
            if not children.isdigit():
                raise SyntaxError, (
                  'Expected the format to be children:label. Where children is '
                  'an int.'
                )
            yield int(children), sym
    return ast.build_tree(g(s))

def assert_file_exists(path):
    '''checks if the file exists. If it doesn't causes the program to exit.
    @param path : path to file
    @returns : the path to the file (an echo) [only on success]
    '''
    path = os.path.abspath(path)
    if not os.path.exists(path):
        log('No file found. "%(path)s"' % locals())
        usage(error_codes['file_not_found'])
    return path

def assert_dir_exists(path):
    '''checks if a directory exists. if not it creates it. if something exists
    and it is not a directory it exits with an error.
    '''
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.mkdir(path)
    elif not os.path.isdir(path):
        log('Expected a directory found a file. "%(path)s"' % locals())
        usage(error_codes['file_instead_of_dir'])
    return path

def read_file_or_die(path):
    '''Reads the file, if there is an error it kills the program.
    @param path : the path to the file
    @returns string : the contents of the file
    '''
    try:
        f = open(path, 'r')
        s = f.read()
        f.close()
    except Exception:
        log('Error reading file at "%s".' % path)
        usage(error_codes['bad_file_read'])
    return s

def split_stdin():
    '''Read the stdin a yield chunks seperated by the blank lines'''
    lines = list()
    for line in sys.stdin.read().split('\n'):
        if not line and lines:
            yield '\n'.join(lines)
            lines = list()
        elif line:
            lines.append(line)
    if lines:
        yield '\n'.join(lines)

def parse_bool(s):
    '''parses s to check it is in [true, false]. returns the appropriate
    bool. If it isn't a book prints error and exits.
    @param s : a string
    @returns bool
    '''
    bools = {'true':True, 'false':False}
    if s not in bools:
        log('Expected bool found "%s"' % (s))
        log('You probably want %s case matters' % str(bools.keys()))
        usage(error_codes['bad_bool'])
    return bools[s]

def show_artifacts(conf):
    '''Print the available artifacts and exit normally.'''
    for name, d in artifacts.engine.filter_artifacts(conf, artifacts.available_artifacts(conf)):
        log(name)
    sys.exit(0)

def parse_artspec(s):
    '''Parses "artspecs" and returns (artifact, outpath). An artspec is the
    just the name of the artifact colon the path where it should be placed.
    If string is not in the artspec langauge print error and exit.

      ie. name:path
      eg. asts:./gramstats/asts/

    @param s : string in outspec format
    @returns : artifact name, path
    '''
    if ':' not in s:
        return s, None
        #log('Expecting an <artspec> got "%s"' % (s))
        #usage(error_codes['bad_artspec'])
    name, path = s.split(':', 1)
    return name, os.path.abspath(path)

def load_coverage(coverage, file_paths):
    if coverage is None: return None
    cov_files = [
        assert_file_exists(path.replace('.ast', '.coverage'))
        for path in file_paths
    ]
    tables = [
        (
          path,
          [
            [col.strip() for col in row.split(',')]
            for row in read_file_or_die(path).split('\n')
          ]
        )
        for path in cov_files
    ]
    return [
        (
          path,
          dict(
            (
              row[0],
              {
                'line_count':int(row[1]),
                'executed_lines':set(int(col) for col in row[2:])
              }
            )
            for row in table
          )
        )
        for path, table in tables
    ]

def main(args):

    try:
        opts, args = getopt(
            args,
            'hvg:o:i:t:aA:T:sE:c',
            [
              'help', 'version', 'grammar=', 'outdir=', 'imgs=', 'tables=',
              'artifacts', 'artifact=', 'usetables=', 'stdin', 'exclude',
              'coverage',
            ]
        )
    except GetoptError, err:
        log(err)
        usage(error_codes['option'])

    stdin = False
    usetables = False
    outdir = './gramstats'
    loadpath = None
    grammar = None
    genimgs = True
    gentables = True
    requested_artifacts = dict()
    excluded = list()
    list_artifacts = False
    coverage = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-v', '--version'):
            version()
        elif opt in ('-g', '--grammar'):
            log('WARNING: -g not yet supported')
            grammar = assert_file_exists(arg)
        elif opt in ('-o', '--outdir'):
            outdir = assert_dir_exists(arg)
        elif opt in ('-i', '--imgs'):
            genimgs = parse_bool(arg)
        elif opt in ('-t', '--tables'):
            gentables = parse_bool(arg)
        elif opt in ('-a', '--artifacts'):
            list_artifacts = True
        elif opt in ('-c', '--coverage'):
            #log('WARNING: -c not yet supported')
            coverage = True
        elif opt in ('-A', '--Artifact'):
            #log('WARNING: -A not yet supported')
            requested_artifacts.update((parse_artspec(arg),))
        elif opt in ('-E', '--exclude'):
            #log('WARNING: -A not yet supported')
            excluded.append(arg)
        elif opt in ('-T', '--usetables'):
            ### log('WARNING: -T not yet supported')
            loadpath = assert_file_exists(arg)
            usetables = True
        elif opt in ('-s', '--stdin'):
            stdin = True

    if coverage is not None and stdin:
        log('Cannot process both coverage and stdin, supply one or the other.')
        usage(error_codes['stdin_and_coverage'])

    if len(args) > 0 and stdin:
        log('Cannot process both files and stdin, supply one or the other.')
        usage(error_codes['stdin_and_files'])

    if not ((len(args) != 0) or (usetables) or (stdin)):
        log('You must provide a list of syntax trees to characterize.')
        usage(error_codes['no_args'])

    file_paths = sorted(assert_file_exists(arg) for arg in args)
    syntax_trees = [mktree(read_file_or_die(path)) for path in file_paths]
    if stdin: syntax_trees += [mktree(tree) for tree in split_stdin()]
    coverage = load_coverage(coverage, file_paths)

    if requested_artifacts:
        genimgs = False
        gentables = False

    if grammar is not None:
        grammar = lib.parse_grammar(read_file_or_die(grammar))


    conf = {'trees':syntax_trees,
            'grammar': grammar,
            'outdir':assert_dir_exists(outdir),
            'loadtables':usetables,
            'loadpath':loadpath,
            'genimgs':genimgs,
            'gentables':gentables,
            'requested_artifacts':requested_artifacts,
            'excluded_artifacts':excluded,
            'coverage':coverage,
            'list_artifacts':list_artifacts,
    }

    if list_artifacts:
        show_artifacts(conf)
    else:
        artifacts.produce(conf)

if __name__ == '__main__':
    main(sys.argv[1:])

