
import sys
from genthemall.version import get_version
from optparse import OptionParser
from genthemall.core import generate, list_templates


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
    parser.add_option('-f', '--config-file',
        default='genthemall.cfg',
        metavar='PATH',
        help="python module file to import, e.g. '../other.cfg'"
    )
    parser.add_option('-t', '--template-folder',
        default='./gt',
        metavar='PATH',
        help="sepecify template folder for use."
    )
    parser.add_option('-l', '--list-templates',
        action='store_true',
        dest='list_templates',
        default=False,
        help='list add template description.'
    )
    opts, args = parser.parse_args()
    return parser, opts, args

def main():
    try:
        parser, options, arguments = parse_options()
        if options.show_version:
            print "GenThemAll version:", get_version('short')
            sys.exit(0)
        if options.list_templates:
            list_templates(options.template_folder)
            sys.exit(0)
        generate(options.config_file, options.template_folder)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(1)
    finally:
        pass
    sys.exit(0)
