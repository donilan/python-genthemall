
import sys, logging
from genthemall.version import get_version
from optparse import OptionParser
from genthemall.core import GTLGenerator, GTLTemplateHolder


def parse_options():
    parser = OptionParser(
        usage = ("genthemall [options]")
        )
    parser.add_option('-V', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show program's version number and exit."
    )
    parser.add_option('-f', '--config-file',
        default='genthemall.cfg',
        metavar='PATH',
        help="python module file to import, e.g. '../other.cfg'."
    )
    parser.add_option('-t', '--template-folder',
        default='./gt',
        metavar='PATH',
        help="sepecify template folder for use."
    )
    parser.add_option('-o', '--output-folder',
        default='./out',
        metavar='PATH',
        help='Sepecify output folder for the generate files.'
    )
    parser.add_option('-l', '--list-templates',
        action='store_true',
        dest='list_templates',
        default=False,
        help='list template description and exit.'
    )
    parser.add_option('-c', '--check-templates',
        action='store_true',
        dest='check_templates',
        default=False,
        help='Verified templates and exit.'
    )
    opts, args = parser.parse_args()
    return parser, opts, args

def main():
    logging.basicConfig()
    try:
        parser, options, arguments = parse_options()
        if options.show_version:
            print "GenThemAll version:", get_version('short')
            sys.exit(0)
        if options.list_templates:
            GTLTemplateHolder(options.template_folder).list_templates()
            sys.exit(0)
        if options.check_templates:
            GTLTemplateHolder(options.template_folder)
            sys.exit(0)
            
#        generate(options.config_file, options.template_folder)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(1)
    finally:
        pass
    sys.exit(0)
