import sys, os
from optparse import OptionParser
from genthemall.utils import load_command, load_function
from genthemall.core import GTLGenerator
import json

class BaseCommand:
    def __init__(self, args):
        self.parser = OptionParser(usage=self._usage, add_help_option=False)
        self.parser.add_option('-f', dest='configFile', 
                               default='genthemall.cfg',
                               help='Specify genthemall config file.')
        self._args = args

    def init_options(self):
        if not hasattr(self, 'opts'):
            (self.opts, self.args) = self.parser.parse_args(self._args)

    def help(self):
        self.parser.print_help()

    def execute(self):
        pass

    def load_config(self):
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
        f = open(self.opts.configFile, 'w')
        f.write(json.dumps(self.load_config(), indent=4))
        f.close()

    def get_module(self, moduleName):
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

    _usage = "%prog project [options] <projectName> <namespace> [displayName]"

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
    _usage = '%prog module <moduleName> <propertyName> <propertyValue>'

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
    
    _usage = '%prog field <moduleName> <filedName> <propertyName> <propertyValue>'

    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=5)

        moduleName = self.args[1]
        fieldName = self.args[2]
        propertyName = self.args[3]
        propertyValue = self.args[4]

        modifyField = self.get_field(moduleName, fieldName)
#        properties = modifyField.setdefault('properties', {})
        modifyField[propertyName] = propertyValue
        
        self.save_config();

class CommandRemove(BaseCommand):
    _usage = '%prog remove <moduleName> [fieldName]'

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

    _usage = '%prog generate <type> <templateName>'
    
    def __init__(self, args):
        BaseCommand.__init__(self, args)
        self.init_options()

    def execute(self):
        self.do_some_check(args_gt_length=3)
        funcName = self.args[1]
        templates = self.args[2:]
        confFn = load_function('genthemall.conf.%s' % funcName)
        config = self.load_config()
        confFn(config)
        print(json.dumps(config, indent=4))
        generator = GTLGenerator(config)
        generator.generate(templates)
