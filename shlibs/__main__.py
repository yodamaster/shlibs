#!/usr/bin/python
import argparse
from . import all_libraries_used

ARGP = argparse.ArgumentParser('shlibs', description=('Print the complete '
    'list of shared libraries used by the specified binary file(s), '
    'including child dependencies'))
ARGP.add_argument('file', nargs='+', help='file(s) to report on')
ARGS = ARGP.parse_args()

ALL_DEPS = reduce(lambda a, b: set(a)|set(b),
                  [all_libraries_used(f) for f in ARGS.file])

for PATH in ALL_DEPS:
    print PATH