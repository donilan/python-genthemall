import logging, os, re, io, sys
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
    def __init__(self, config, template_folder = None, gtl_template_holder = None, out_dir = 'out'):
        self.outDir = out_dir
        self.config = config
        if gtl_template_holder and isinstance(gtl_template_holder \
            , GTLTemplateHolder):
            self.gtlTemplateHolder = gtl_template_holder
        else:
            self.gtlTemplateHolder = GTLTemplateHolder(template_folder)

    def generate(self, template, dest):
        """Generate with sepecify template names."""
        if self.config is None or self.gtlTemplateHolder is None:
            log.error('Config load fail or Template load fail.')
            return False

        t = self.gtlTemplateHolder.find_template_by_name(template)
        if t is None:
            log.error('Template name[%s] not found' % template)
            sys.exit(1)

        self._generate_by_template(t, dest)
        
    def _generate_by_template(self, template, dest):
        for module in self.config.get('modules', []):
            content = MakoTemplate(filename=template).render( \
                config=self.config, module=module)
            if self._generate_to_file(content, template, dest):
                succ_counter += 1
            else: 
                fail_counter += 1
        return (succ_counter, fail_counter)

    def _generate_to_file(self, content, template, dest):
        """Generate content and write to file."""
        dest = MakoTemplate(dest).render(config=self.config, module=module)
        dest = os.path.join(self.outDir, dest)
        log.info('Generating [%s]' % dest)
        destDir = os.path.dirname(dest)
        if not os.path.exists(destDir):
            log.info('Dir [%s] not exists, create.' % destDir)
            os.makedirs(destDir)
        file = open(dest, 'w')
        file.write(content)
        file.close()
        return True
### class GTLGenerator
