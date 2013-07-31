#!/usr/bin/python
"""
Print the complete list of shared libraries used by the specified binary
file(s) including any child dependencies.
"""
import subprocess
import os
import macholib.MachO
import macholib.mach_o
#import pdb


def resolve_rpath(binary_path, rpath_spec, loader_path=None):
    """
    Return a resolved filesystem path for a given rpath-based library path 

    This code is mostly copied from rpath.list_rpaths @:
    https://github.com/enthought/machotools/tree/master/machotools
    """
    if loader_path is None:
        loader_path = binary_path

    rpaths = []

    mach_object = macholib.MachO.MachO(binary_path)
    for header in mach_object.headers:
        header_rpaths = []
        rpath_commands = [command for command in header.commands
                          if isinstance(command[1],
                                        macholib.mach_o.rpath_command)]
        for rpath_command in rpath_commands:
            rpath = rpath_command[2]
            if not rpath.endswith("\x00"):
                raise ValueError(("Unexpected end character for rpath "
                                  "command value: %r").format(rpath))
            else:
                header_rpaths.append(rpath.rstrip(b'\x00'))
        rpaths.append(header_rpaths)

    # Some shortcuts for speed and readability
    normpath = os.path.normpath

    for rpaths_for_arch in rpaths:
        for rpath_entry in rpaths_for_arch:
            if rpath_entry.startswith('@'):
                rpath_entry = expand_load_variables(rpath_entry, binary_path,
                                                    loader_path)
            test_path = normpath(rpath_spec.replace("@rpath", rpath_entry, 1))

            if os.path.exists(test_path):
                return test_path

    # pdb.set_trace()
    return None


def expand_load_variables(path_spec, binary_path, loader_path=None):
    if loader_path is None:
        loader_path = binary_path
    
    # Some shortcuts for speed and readability
    normpath = os.path.normpath
    dirname = os.path.dirname

    result = path_spec
    if path_spec.startswith("@executable_path"):
        result = normpath(path_spec.replace("@executable_path",
                                            dirname(binary_path), 1))
    elif path_spec.startswith("@loader_path"):
        result = normpath(path_spec.replace("@loader_path",
                                            dirname(loader_path), 1))
    elif path_spec.startswith("@rpath"):
        result = resolve_rpath(binary_path, path_spec, loader_path)

    return result


def libraries_used(target_path, loader_path):
    """
    Return a list of the paths of the shared libraries used by the object file
    (or executable) at the specified target_path
    """
    raw_output = subprocess.check_output(['otool', '-L', target_path],
                                         stderr=subprocess.STDOUT)
    # We can expect output like this:
    # [tab]path_possibly_with_spaces[space][open paren]some_junk[close paren]
    result = []

    for line in raw_output.splitlines():
        if line[0] == '\t':
            lib = line.rsplit('(', 1)[0].strip()
            if lib.startswith('@'):
                # print "will expand {}".format(lib)
                lib = expand_load_variables(lib, loader_path)
            if lib != target_path:
                result.append(lib)

    return result if result else None




