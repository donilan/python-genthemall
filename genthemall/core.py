import logging, os, re, io, sys, json
from mako.template import Template as MakoTemplate
from config import Config
from genthemall.utils import copyfiles

__version__ = '0.3.0'

def get_version():
    return __version__

log = logging.getLogger('genthemall.core')

class GTLTemplateHolder():
    
    def __init__(self, folder = './.genthemall'):
        self.folder = folder
        self.templates = []
        self._find_template_files()

    def copy_templates_to_workspace(self):
        src = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gt')
        log.debug('Copy [%s] to [%s]' % (src, self.folder))
        copyfiles(src, self.folder)

    def _find_template_files(self):
        """Find template files ."""
        if not os.path.exists(self.folder):
            log.info('Template folder [%s] not found, then create and copy system template in it.' % self.folder)
            self.copy_templates_to_workspace()
        self.templates = []
        for (root, dirs, files) in os.walk(self.folder):
            for f in files:
                if f.endswith('.gt'):
                    self.templates.append((f[:-3], os.path.join(root, f)))

    def list_templates(self):
        """List all template we found, and print them on terminal."""
        print 'GenThemAll %s List all templates.\n' % get_version()
        for idx, t in enumerate(self.templates):
            print '%02d. %30s' % ((idx+1), t[0])

    def find_template_by_name(self, name):
        """Find sepecify template by name."""
        for t in self.templates:
            if t[0] == name:
                return t[1]
        return None

    def find_all_templates(self):
        return [t[1] for t in self.templates]

### GTLTemplateHolder

class GTLGenerator():
    """GTLGenerator"""
    def __init__(self, config, template_folder = None, gtl_template_holder = None\
                 , out_dir = 'out', one_file = False):
        self.outDir = out_dir
        self.config = config
        self.oneFile = one_file
        if gtl_template_holder and isinstance(gtl_template_holder \
            , GTLTemplateHolder):
            self.gtlTemplateHolder = gtl_template_holder
        else:
            self.gtlTemplateHolder = GTLTemplateHolder(template_folder)

    def generate(self, tmpl_name, dest):
        """Generate with sepecify template names."""
        if self.config is None or self.gtlTemplateHolder is None:
            log.error('Config load fail or Template load fail.')
            sys.exit(1)

        template = self.gtlTemplateHolder.find_template_by_name(tmpl_name)
        if template is None:
            log.error('Template name[%s] not found' % tmpl_name)
            sys.exit(1)

        dest = os.path.join(self.outDir, dest)

        # Just generate a file if oneFile be setted.
        if self.oneFile:
            self._generate_to_file(template, dest, config=self.config)
            return

        for module in self.config.get('modules', []):
            self._generate_to_file(template, dest, config=self.config, module=module)


    def _generate_to_file(self, tmpl_file_name, dest, **data):
        out = MakoTemplate(dest).render(**data)
        destDir = os.path.dirname(out)
        if not os.path.exists(destDir):
            log.info('Dir [%s] not exists, create.' % destDir)
            os.makedirs(destDir)
        log.info('Generating [%s]' % out)
        tmpl = MakoTemplate(filename=tmpl_file_name)
        content = tmpl.render(**data)
        file = open(out, 'w')
        file.write(content)
        file.close()
### class GTLGenerator


### class GTLConfig
class GTLConfig:
    
    def __init__(self, config_file):
        self.configFile = config_file
        content = '{}'
        if os.path.exists(config_file):
            f = open(config_file)
            content = f.read()
            if len(content) == 0:
                content = '{}'
            f.close()
        self.conf = json.loads(content)
            
    def save(self):
        """
        Save config to file.
        """
        f = open(self.configFile, 'w')
        f.write(json.dumps(self.conf, indent=4))
        f.close()

    def get_module(self, moduleName):
        """
        Get module by module name from config file.
        """
        modules = self.conf.setdefault('modules', [])
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
### END class GTLConfig
