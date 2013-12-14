import logging, os, re, io, sys
from mako.template import Template as MakoTemplate
from config import Config

__version__ = '0.2.0'

def get_version():
    return __version__

log = logging.getLogger('genthemall.core')

class GTLTemplate:
    """Template object for store in application runtime."""
    def __init__(self, config, content, path):
        self.config = config
        self.content = content
        self.path = path

class GTLTemplateHolder():
    
    def __init__(self, folder = None):
        self.user_template_folder = folder
        self.sys_template_folder = os.path.join(os.path.abspath(\
            os.path.dirname(__file__)), 'gt')
        self.user_template_files = []
        self.sys_template_files = []
        self.user_templates = []
        self.sys_templates = []
        self._init_templates()

    def _init_template_files(self):
        """Find template files on user sepecify folder and 
        genthemall default folder."""
        def finder_fn(_folder):
            _files = []
            for root, dirs, files in os.walk(_folder):
                for file in files:
                    if file.endswith(".gt"):
                        _files.append(os.path.join(root, file))
                        
            return _files
        self.sys_template_files = finder_fn(self.sys_template_folder)
        if self.user_template_folder:
            self.user_template_files = finder_fn(self.user_template_folder)

    def list_templates(self):
        """List all template we found, and print them on terminal."""
        print 'GenThemAll %s List all templates.\n' % get_version()
        def list_fn(templates, prefix_msg):
            print prefix_msg
            for idx, t in enumerate(templates):
                print '%02d. %30s [v %s]' % ((idx+1), t.config.name, \
                    t.config.version)
        list_fn(self.sys_templates, 'GenThemAll default templates:')
        if self.user_templates:
            list_fn(self.user_templates, 'User templates:')

    def find_template_by_name(self, name):
        """Find sepecify template by name."""
        for t in self.sys_templates + self.user_templates:
            if t.config.name == name:
                return t
        return None
    def find_all_templates(self):
        return self.sys_templates + self.user_templates

    def _init_templates(self):
        self._init_template_files()
        """Find template files and make it in to Template."""
        def make_fn(template_files):
            templates = []
            for f in template_files:
                content = open(f).read()
                match = re.search(r'<%[^%]+%>' ,content)
                if match:
                    config_str = match.group()
                    content_str = content.replace(config_str, '')
                    config_str = config_str[2:-2]

                    config = Config(io.BytesIO(config_str))
                    t = self._make_template(config, content_str, f)
                    if t is not None:
                        templates.append(t)
            return templates
        self.sys_templates = make_fn(self.sys_template_files)
        if self.user_template_files:
            self.user_templates = make_fn(self.user_template_files)

    def _make_template(self, config, content, path):
        """Make template from config and content, check 
        config attribute before make. some attribute must be set, 
        if not return None."""
        if config is not None and content is not None:
            return GTLTemplate(config, content, path)
        return None

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

    def generate(self, template_names):
        """Generate with sepecify template names."""
        if self.config is None or self.gtlTemplateHolder is None:
            log.error('Config load fail or Template load fail.')
            return False
        if template_names is None or len(template_names) < 1:
            log.error('Param template_names cannot be null or empty')
            return False
        if isinstance(template_names, str):
            template_names = [t.strip() for t in template_names.split(',')]
        if not isinstance(template_names, list):
            log.error('Param template_names connot convert to list')
            return False
        succ_counter = 0
        fail_counter = 0
        templates = []
        for t_name in template_names:
            if t_name == 'all':
                templates = self.gtlTemplateHolder. \
                            find_all_templates()
                break
            t = self.gtlTemplateHolder.find_template_by_name(\
                    t_name)
            if t is None:
                log.warn('Template name[%s] not found' % t_name)
                fail_counter += 1
                continue
            templates.append(t)
            
        for t in templates:
            if self._generate_by_template(t):
                succ_counter += 1
            else:
                fail_counter += 1
        return (succ_counter, fail_counter)
        
    def _generate_by_template(self, template):
        succ_counter = 0
        fail_counter = 0
        for module in self.config.get('modules', []):

            content = MakoTemplate(template.content).render( \
                config=self.config, module=module)
            if self._generate_to_file(content, template, module):
                succ_counter += 1
            else: 
                fail_counter += 1
        return (succ_counter, fail_counter)

    def _generate_to_file(self, content, template, module):
        """Generate content and write to file."""
        dest = MakoTemplate(template.config.dest).render( \
            config=self.config, module=module)
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
