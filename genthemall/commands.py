import sys, os, logging, json
from optparse import OptionParser
from genthemall.utils import load_command, load_function
from genthemall.core import GTLGenerator, GTLTemplateHolder

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
            default='./gt', metavar='PATH',
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

    def load_config(self):
        """
        Load config file and just load once.
        """
        if hasattr(self, 'conf'):
            return self.conf
        if os.path.exists(self.opts.configFile):
            f = open(self.opts.configFile)
            content = f.read()
            if len(content) == 0:
                content = '{}'
            self.conf = json.loads(content)
            f.close()
        else:
            self.conf = json.loads('{}')
        return self.conf

    def save_config(self):
        """
        Save config to file.
        """
        f = open(self.opts.configFile, 'w')
        f.write(json.dumps(self.load_config(), indent=4))
        f.close()

    def get_module(self, moduleName):
        """
        Get module by module name from config file.
        """
        config = self.load_config()
        modules = config.setdefault('modules', [])

        modifyModule = None
        for module in modules:
            if module.get('name') == moduleName:
                modifyModule = module
                break
        if modifyModule is None:
            modifyModule = {}
            modules.append(modifyModule)
            modifyModule['name'] = moduleName
        return modifyModule

    def get_field(self, moduleName, fieldName):
        """
        Get field by module name and field name from config file.
        """
        modifyModule = self.get_module(moduleName)
        fields = modifyModule.setdefault('fields', [])
        modifyField = None
        for f in fields:
            if f.get('name', '') == fieldName:
                modifyField = f
                break
        if modifyField is None:
            modifyField = {}
            modifyField['name'] = fieldName
            fields.append(modifyField)
        return modifyField

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

        conf = self.load_config()

        conf['projectName'] = projectName
        conf['namespace'] = namespace
        conf['displayName'] = displayName
        self.save_config()

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
        module = self.get_module(moduleName)
        module[propertyName] = propertyValue
        self.save_config()
        
class CommandField(BaseCommand):
    
    _usage = '%prog field <moduleName> <filedName> <propertyName>=<propertyValue>... [options]'

    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=4)

        moduleName = self.args[1]
        fieldName = self.args[2]


        modifyField = self.get_field(moduleName, fieldName)
        for p in self.args[3:]:
            prop = p.split('=')
            if len(prop) == 2:
                modifyField[prop[0]] = prop[1]
            else:
                self.help()
                sys.exit(1)
        
        self.save_config();

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

        config = self.load_config()
        module = self.get_module(moduleName)

        if fieldName is not None:
            f = self.get_field(moduleName, fieldName)
            module.get('fields', []).remove(f)
        else:
            config.get('modules', []).remove(module)
            
        self.save_config()
        
class CommandGenerate(BaseCommand):

    _usage = '%prog generate <type> <templateName>... [options]'
    
    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.add_option_template()
        self.add_option_output_folder()
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=3)
        funcName = self.args[1]
        templates = self.args[2:]
        confFn = load_function('genthemall.conf.%s' % funcName)
        config = self.load_config()
        confFn(config)
        generator = GTLGenerator(config=config, \
                                 template_folder=self.opts.template_folder,\
                                 out_dir=self.opts.output_folder)
        generator.generate(templates)


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
            if os.environ.get('EDITOR', None) is not None:
                os.system('$EDITOR %s' % tmpl.path)
            else:
                log.error('Env EDITOR not set.')
                sys.exit(1)
