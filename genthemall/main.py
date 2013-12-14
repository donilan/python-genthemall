#!/usr/bin/env python

import sys, logging, os, importlib
from optparse import OptionParser
from genthemall.utils import load_command

USAGE = """usage: genthemall <command> [<args>]

 project    add or modify project property.
 module     add or modify module command property.
 filed      add or modify filed properties.
 generate   generate files using MakoTemplate.
 template   List or edit some template file.
 help       show command help info.
"""

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    cmdName = sys.argv[1]
    CmdClass = load_command(cmdName)
    cmd = CmdClass(sys.argv[1:])
    cmd.execute()

