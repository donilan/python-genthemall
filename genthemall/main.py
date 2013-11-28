
import sys
from genthemall.version import get_version
from optparse import OptionParser


def parse_options():
    parser = OptionParser(
        usage = ("genthemall [options]")
        )
    parser.add_option('-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit"
    )
    parser.add_option('-f', '--file',
        default='genthemall.py',
        metavar='PATH',
        help="python module file to import, e.g. '../other.py'"
    )
    opts, args = parser.parse_args()
    return parser, opts, args

def main():
    try:
        parser, options, arguments = parse_options()
        print options
        if options.show_version:
            print "GenThemAll version:", get_version('short')
            sys.exit(0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(1)
    finally:
        pass
    sys.exit(0)
