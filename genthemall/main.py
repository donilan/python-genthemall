#!/usr/bin/env python

import sys, logging, os, importlib
from optparse import OptionParser
from genthemall.utils import load_command

USAGE = """usage: genthemall <command> [<args>]

 project     Add or modify project property.
 module      Add or modify module command property.
 filed       Add or modify filed properties.
 remove      Remove specify module or field.
 generate    generate files using MakoTemplate.
 template    List or edit some template file.
 printConfig Print sepecify type config.
 help        show command help info.
"""

def main():
    """
    We begin here.
    """
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

#    logging.basicConfig(level=logging.INFO)
    cmdName = sys.argv[1]
    CmdClass = load_command(cmdName)
    cmd = CmdClass(sys.argv[1:])
    cmd.execute()

