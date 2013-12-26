import sys, os, logging, json
from optparse import OptionParser
from genthemall.utils import load_command, load_function, transform_config
from genthemall.core import GTLGenerator, GTLTemplateHolder, GTLConfig

log = logging.getLogger('genthemall.command')

class BaseCommand:
    def __init__(self, args):
        self.parser = OptionParser(usage=self._usage, add_help_option=False)
        self.parser.add_option(
            '-f', '--config-file', dest='configFile', 
            default='genthemall.cfg', metavar='PATH',
            help='Sepecify config file for use, e.g. "../other.cfg". Default is genthemall.cfg')
        self.parser.add_option(
            '-v', '--verbose', action='count', dest='verbose',
            help='Increase verbosity (specify multiple times for more).')
        self._args = args

    def add_option_template(self):
        self.parser.add_option(
            '-t', '--template-folder',
            default='./.genthemall', metavar='PATH',
            help='sepecify template folder for use.')

    def add_option_output_folder(self):
        self.parser.add_option(
            '-o', '--output-folder',
            default='./out', metavar='PATH',
            help='Sepecify output folder for the generate files.')

    def init_options(self):
        """
        Parser user options and init logging level
        """
        if not hasattr(self, 'opts'):
            (self.opts, self.args) = self.parser.parse_args(self._args)
            log_level = logging.WARNING # default
            if self.opts.verbose == 1:
                log_level = logging.INFO
            elif self.opts.verbose >= 2:
                log_level = logging.DEBUG
            logging.basicConfig(level=log_level)

    def help(self):
        """
        Print help message.
        """
        self.parser.print_help()

    def execute(self):
        """
        The method for execute, Sub class need implement the method.
        """
        pass

    def do_some_check(self, args_gt_length=0):
        """
        Just do some check, It's ugly, so need change, but now I don't know how, just no idea.
        """
        if not os.path.exists(self.opts.configFile):
            print('Config file [%s] not found. Please check or use genthem project command to create one.' % self.opts.configFile)
            sys.exit(1)
        if len(self.args) < args_gt_length:
            self.help()
            sys.exit(1)

class CommandHelp(BaseCommand):
    _usage = 'genthemall help <command>'

    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.args = args

    def execute(self):
        if len(self.args) < 2:
            print self._usage
        else:
            cmdClass = load_command(self.args[1])
            cmd = cmdClass(None)
            cmd.help()


class CommandProject(BaseCommand):

    _usage = "%prog project [options] <projectName> <namespace> [displayName] [options]"

    def __init__(self, args):
        BaseCommand.__init__(self, args)

        self.init_options()

    def execute(self):
        if len(self.args) < 3:
            self.help()
            sys.exit(1)
        projectName = self.args[1]
        namespace = self.args[2]
        displayName = ''
        if len(self.args) > 3:
            displayName = self.args[3]

        gtlConfig = GTLConfig(self.opts.configFile)
        conf = gtlConfig.conf
        conf['projectName'] = projectName
        conf['namespace'] = namespace
        conf['displayName'] = displayName
        gtlConfig.save()

class CommandModule(BaseCommand):
    _usage = '%prog module <moduleName> <propertyName> <propertyValue> [options]'

    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=4)
        moduleName = self.args[1]
        propertyName = self.args[2]
        propertyValue = self.args[3]
        gtlConfig = GTLConfig(self.opts.configFile)
        module = gtlConfig.get_module(moduleName)
        module[propertyName] = propertyValue
        gtlConfig.save()
        
class CommandField(BaseCommand):
    
    _usage = '%prog field <moduleName> <filedName> <propertyName>=<propertyValue>... [options]'

    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=4)

        moduleName = self.args[1]
        fieldName = self.args[2]

        gtlConfig = GTLConfig(self.opts.configFile)
        modifyField = gtlConfig.get_field(moduleName, fieldName)
        for p in self.args[3:]:
            prop = p.split('=')
            if len(prop) == 2:
                modifyField[prop[0]] = prop[1]
            else:
                self.help()
                sys.exit(1)
        
        gtlConfig.save()

class CommandRemove(BaseCommand):
    _usage = '%prog remove <moduleName> [fieldName] [options]'

    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=2)
        moduleName = self.args[1]
        fieldName = None
        if len(self.args) > 2:
            fieldName = self.args[2]

        gtlConfig = GTLConfig(self.opts.configFile)
        config = gtlConfig.conf
        module = gtlConfig.get_module(moduleName)

        if fieldName is not None:
            f = gtlConfig.get_field(moduleName, fieldName)
            module.get('fields', []).remove(f)
        else:
            config.get('modules', []).remove(module)
            
        gtlConfig.save()
        
class CommandGenerate(BaseCommand):

    _usage = '%prog generate <templateName> <dest> [options]'
    
    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.add_option_template()
        self.add_option_output_folder()
        self.parser.add_option(
            '-l', '--one-file', default=False,
            action='store_true',
            help='Just generate a file.')
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=3)
        template = self.args[1]
        dest = self.args[2]
        gtlConfig = GTLConfig(self.opts.configFile)
        config = gtlConfig.conf
        typeIdx = template.find('.')
        if typeIdx == -1:
            log.error('template name must be "type.templatename".')
            sys.exit(1)
        transform_config(config, template[:typeIdx])
        generator = GTLGenerator(
            config=config, template_folder=self.opts.template_folder,
            out_dir=self.opts.output_folder, one_file=self.opts.one_file)
        log.debug('Generator init done, and using config type [%s].' \
                  % template[:typeIdx])
        generator.generate(template, dest)


class CommandTemplate(BaseCommand):

    _usage = """%prog template <command> [args] [options]
  list    List all templates
  edit    edit template using $EDITOR
"""
    
    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.add_option_template()
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=2)
        cmd = self.args[1]

        holder = GTLTemplateHolder(folder=self.opts.template_folder)
        if cmd == 'list':
            holder.list_templates()
        elif cmd == 'edit':
            if len(self.args) < 3:
                log.error('Please sepecify template name for edit.')
                sys.exit(1)
            tmpl = holder.find_template_by_name(self.args[2])
            if tmpl is None:
                log.warn('Template name [%s] not exists.' % self.args[2])
                sys.exit(1)
            if os.environ.get('EDITOR', None) is not None:
                os.system('$EDITOR %s' % tmpl)
            else:
                log.error('Env EDITOR not set.')
                sys.exit(1)

class CommandPrintConfig(BaseCommand):
    _usage = """%prog printConfig <type> [options]"""
        
    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=2)
        _type = self.args[1]
        gtlConfig = GTLConfig(self.opts.configFile)
        config = gtlConfig.conf
        transform_config(config, _type)
        print(json.dumps(config, indent=4))
