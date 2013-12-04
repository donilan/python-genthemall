import logging, os, re, io, sys
from config import Config, Sequence, Mapping
from genthemall.version import get_version
from mako.template import Template as MakoTemplate

__version__ = '0.1.0-dev'

def get_version():
    return __version__

log = logging.getLogger('genthemall.core')

default_max_map = {
    'long': 1 << 64,
    'int': 1 << 32,
    'string': 256,
    'text': 1024,
    'date': None,
}

default_min_map = {
    'long': -1 << 64,
    'int': -1 << 32,
    'string': 0,
    'text': 0,
    'date': None,
}

java_type_map = {
        'long': 'java.lang.Long',
        'int': 'java.lang.Integer',
        'string': 'java.lang.String',
        'text': 'java.lang.String',
        'date': 'java.util.Date',
}
java_short_type_map = {
        'long': 'long',
        'int': 'int',
        'string': 'String',
        'text': 'String',
        'date': 'java.util.Date',
}
database_type_map = {
        'long': 'NUMBER',
        'int': 'NUMBER',
        'string': 'VARCHAR2',
        'text': 'VARCHAR2',
        'date': 'DATETIME',
}

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

### GTLTemplateHolder

class GTLGenerator():
    """GTLGenerator"""
    def __init__(self, config_file = 'genthemall.cfg', template_folder = None, gtl_template_holder = None, out_dir = 'out'):
        self.outDir = out_dir
        self.config = None
        if gtl_template_holder and isinstance(gtl_template_holder \
            , GTLTemplateHolder):
            self.gtlTemplateHolder = gtl_template_holder
        else:
            self.gtlTemplateHolder = GTLTemplateHolder(template_folder)
        self.config_file = config_file
        self._load_config(config_file)

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
        for module in self.config.modules:
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


    def _load_config(self, config_file):
        """Load config file convert to python object."""
        log.debug('Loading config file[%s]...', config_file)
        self.config = Config(config_file)
        if not hasattr(self.config, 'modules'):
            log.warn('Module in config file must have modules property.')   
        else:
            self._init_modules_config(self.config.modules)

    def _init_modules_config(self, modules):
        """Init module properties, Add property pascalName, camelName, tableName to module."""
        for m in modules:
            msg_tmpl = 'Module in config file must have [%%s] property.'
            msg_list = []
            if not hasattr(m, 'name'):
                msg_list.append(msg_tmpl % 'name')
            if not hasattr(m, 'properties'):
                msg_list.append(msg_tmpl % 'properties')
            if msg_list:
                log.warn('\n'.join(msg_list))
            else:
                if not hasattr(m, 'pascalName'):
                    m.pascalName = _to_pascal_name(m.name)
                if not hasattr(m, 'camelName'):
                    m.camelName = _to_camel_name(m.name)
                if not hasattr(m, 'tableName'):
                    m.tableName = _to_upper_name(m.name)
            
            if not self._check_module_properties(m.properties):
                continue


    def _check_module_properties(self, properties):
        for p in properties:
            msg_tmpl = 'Must have [%%s] property in properties.'
            if not hasattr(p, 'name'):
                log.warn(msg_tmpl % 'name')
                return False
            else:
                if not hasattr(p, 'pascalName'):
                    p.pascalName = _to_pascal_name(p.name)
                if not hasattr(p, 'camelName'):
                    p.camelName = _to_camel_name(p.name)
                if not hasattr(p, 'columnName'):
                    p.columnName = _to_upper_name(p.name)

            if not hasattr(p, 'type'):
                log.warn(msg_tmpl % 'type')
                return False
                
            else:
                p.javaType = java_type_map[p.type]
                p.javaShortType = java_short_type_map[p.type]
                p.databaseType = database_type_map[p.type]
                if not hasattr(p, 'min'):
                    p.min = default_min_map[p.type]
                if not hasattr(p, 'max'):
                    p.max = default_max_map[p.type]
            
        return True

    def print_config(self, obj = None, i = 0):
        """Print config string in format."""
        if obj == None:
            self.print_config(self.config)
            return
        for k in obj:
            if isinstance(k, str) and isinstance(obj[k], str):
                print u'%s%-20s: %s' % (u' '*i, k, obj[k].decode('utf-8'))
            elif isinstance(k, str) and isinstance(obj[k], \
                                                  Sequence):
                self.print_config(obj[k], i+1)
                print ''
            elif isinstance(k, Mapping):
                self.print_config(k, i+1)
                print ''

### class GTLGenerator


def _to_camel_name(name):
    """
    Convert name to camel name.
    example:
    SysUser will convert to sysUser
    SysRole will convert to sysRole
    """
    if name is not None and len(name) > 1:
        return name[0].lower() + name[1:]
    return name

def _to_pascal_name(name):
    """
    Convert name to pascal name.
    example:
    sysUser will convert to SysUser
    sysRole will convert to SysRole
    """
    if name is not None and len(name) > 1:
        return name[0].upper() + name[1:]
    return name

def _to_upper_name(name):
    """
    Convert name to uppercase name. 
    example: 
    sysUser will convert to SYS_USER
    sysRole will convert to SYS_ROLE
    """
    if name is not None and len(name) > 1:
        u_name = ''
        for s in name:
            if s == s.upper():
                u_name += '_' + s
            else:
                u_name += s.upper()
        return u_name
    return name
