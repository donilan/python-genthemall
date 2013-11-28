
import sys
from genthemall.version import get_version
from optparse import OptionParser


def parse_options():
    parser = OptionParser(
        usage = ("genthemall [options] [genthemall.py]")
        )
    parser.add_option('-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit"
    )
    opts, args = parser.parse_args()
    return parser, opts, args

def main():
    try:
        parser, options, arguments = parse_options()
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
