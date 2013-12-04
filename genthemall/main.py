
import sys, logging, os
from optparse import OptionParser
from genthemall.core import GTLGenerator, GTLTemplateHolder, get_version


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
        help="Sepecify config file for use, e.g. '../other.cfg'. Default is genthemall.cfg"
    )
    parser.add_option('-t', '--template-folder',
        default='./gt',
        metavar='PATH',
        help="sepecify template folder for use."
    )
    parser.add_option('-s', '--sepecify-templates',
        default='all',
        metavar='TMPL1,TMPL2,TMPL3',
        help="sepecify template for generate."
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
    parser.add_option('-p', '--print-config',
        action='store_true',
        dest='print_config',
        default=False,
        help='Print the all config and exit.'
    )
    parser.add_option('-v', '--verbose',
        action='count',
        dest='verbose',
        help='Increase verbosity (specify multiple times for more).'
    )
    opts, args = parser.parse_args()
    return parser, opts, args

def main():
    try:
        parser, options, arguments = parse_options()
        log_level = logging.WARNING # default
        if options.verbose == 1:
            log_level = logging.INFO
        elif options.verbose >= 2:
            log_level = logging.DEBUG
        logging.basicConfig(level=log_level)

        if options.show_version:
            print "GenThemAll version:", get_version()
            sys.exit(0)
        if options.list_templates:
            GTLTemplateHolder(options.template_folder).list_templates()
            sys.exit(0)
        if options.check_templates:
            GTLTemplateHolder(options.template_folder)
            sys.exit(0)
        
        if not os.path.exists(options.config_file):
            print 'Config file [%s] not found.' % options.config_file
            sys.exit(1)

        if options.print_config:
            GTLGenerator(config_file=options.config_file) \
                .print_config()      
            sys.exit(0)

        GTLGenerator(config_file=options.config_file, \
            template_folder=options.template_folder, \
            out_dir=options.output_folder) \
            .generate(options.sepecify_templates)

    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(1)
    finally:
        pass
    sys.exit(0)
