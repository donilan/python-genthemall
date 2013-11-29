import logging, os, re, io
from config import Config
from genthemall.version import get_version
from mako.template import Template as MakoTemplate

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
        print 'GenThemAll %s List all templates.\n' % get_version('short')
        def list_fn(templates, prefix_msg):
            print prefix_msg
            for idx, t in enumerate(templates):
                print '%02d. %30s [v %s]' % ((idx+1), t.config.name, \
                    t.config.version)
        list_fn(self.sys_templates, 'GenThemAll default templates:')
        if self.user_templates:
            list_fn(self.user_templates, 'User templates:')

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
            attr_warn_msg = 'Template file [%s] must have attribute [%%s].' \
                    % os.path.basename(path)                        
            if not hasattr(config, 'name'):
                log.warn(attr_warn_msg % 'name')
            elif config.name in [t.config.name for t in self.sys_templates]:
                log.warn('Template [%s] already in SysTemplate holder, pleace modify your template name, and try again.' % config.name)
            elif not hasattr(config, 'version'):
                log.warn(attr_warn_msg % 'version')
            elif not hasattr(config, 'dest'):
                log.warn(attr_warn_msg % 'dest')
            else:
                return GTLTemplate(config, content, path)
        return None


class GTLGenerator():

    def __init__(self, config_file = 'genthemall.cfg', template_folder = None,
        gtl_template_holder = None):
        self.config = None
        if gtl_template_holder and isinstance(gtl_template_holder \
            , GTLTemplateHolder):
            self.gtlTemplateHolder = gtl_template_holder
        else:
            self.gtlTemplateHolder = GTLTemplateHolder(template_folder)
        self._load_config(config_file)
        

    def _load_config(self, config_file):
        """Load config file convert to python object."""
        log.debug('Loading config file[%s]...', config_file)
        self.config = Config(config_file)
