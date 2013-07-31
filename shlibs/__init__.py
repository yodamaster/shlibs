#!/usr/bin/python
"""
Print the complete list of shared libraries used by the specified binary
file(s) including any child dependencies.
"""
import sys

if sys.platform == 'darwin':
    from .shlibs_darwin import libraries_used
elif sys.platform.startswith('linux'):
    from .shlibs_linux2 import libraries_used
else:
    raise EnvironmentError(
        "I don't have support for {}, yet.".format(sys.platform))


def memoize(function):
    """
    memoization where only the first argument matters
    """
    class FirstArgMemoize(object):
        """ memoization where only the first argument matters """
        cache = None

        def __init__(self):
            self.cache = dict()

        def __getitem__(self, *key):
            if key[0] not in self.cache:
                self.cache[key[0]] = function(*key)
            return self.cache[key[0]]

    return FirstArgMemoize().__getitem__

libraries_used = memoize(libraries_used)

def all_libraries_used(binary_path):
    """
    Return a list of the paths of the shared libraries used by the object file
    (or executable) at the specified binary_path AND ALL SHARED LIBRARIES
    WHICH THEY USE
    """
    visited = dict()

    def reentrant_resolve(path):
        """ This sub-function is re-entered to perform the nested lookups """
        result = [path]
        visited[path] = True
        dependencies = libraries_used(path, binary_path)
        if dependencies is not None:
            for dep in dependencies:
                if dep not in visited:
                    result.extend(reentrant_resolve(dep))
        return result

    return reentrant_resolve(binary_path)


if __name__ == '__main__':
    import argparse

    ARGP = argparse.ArgumentParser(description=('Print the complete list of '
        'shared libraries used by the specified binary file(s), including '
        'child dependencies'))
    ARGP.add_argument('file', nargs='+', help='file(s) to report on')
    ARGS = ARGP.parse_args()

    ALL_DEPS = reduce(lambda a, b: set(a)|set(b),
                      [all_libraries_used(f) for f in ARGS.file])

    for PATH in ALL_DEPS:
        print PATH
