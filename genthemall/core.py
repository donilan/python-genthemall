import logging, os, re, io
from config import Config
from genthemall.version import get_version
from mako.template import Template as MakoTemplate

log = logging.getLogger('genthemall.core')

class Template:
    """Template object for store in application runtime."""
    def __init__(self, config, content):
        self.config = config
        self.content = content

def make_template(config, content, path):
    """Make template from config and content, check config attribute before make. some attribute must be set, if not return None."""
    if config is not None and content is not None:
        attr_warn_msg = 'Template file [%s] must have attribute [%%s].' \
            % os.path.basename(path)                        
        if not hasattr(config, 'name'):
            log.warn(attr_warn_msg % 'name')
        elif not hasattr(config, 'version'):
            log.warn(attr_warn_msg % 'version')
        else:
            return Template(config, content)
    return None

def generate(config_file, folder = None):
    """GenThemAll generate method."""
    print find_templates(folder)

def list_templates(folder = None):
    templates = find_templates(folder)
    print 'GenThemAll %s List all templates.\n' % get_version('short')
    for idx, t in enumerate(templates):
        print '%02d. %30s [v %s]' % ((idx+1), t.config.name, t.config.version)

def find_templates(folder = None):
    """Find template files and make it in to Template."""
    template_files = find_template_files(folder)
    templates = []
    for f in template_files:
        content = open(f).read()
        match = re.search(r'<%[^%]+%>' ,content)
        if match:
            config_str = match.group()
            content_str = content.replace(config_str, '')
            config_str = config_str[2:-2]
            config = Config(io.BytesIO(config_str))
            t = make_template(config, content_str, f)
            if t is not None:
                templates.append(t)
    return templates

def find_template_files(folder = None):
    """Find template files from sepecify folder."""
    folders = find_template_folders(folder)
    _files = []
    for _folder in folders:
        for root, dirs, files in os.walk(_folder):
            for file in files:
                if file.endswith(".gt"):
                    _files.append(os.path.join(root, file))
    log.debug('Found [%d ] template files.' % len(_files))
    return _files


def find_template_folders(folder = None):
    """Find template folders from sepecify folder."""
    gt_paths = []
    gt_paths.append(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gt'))
    if folder is not None:
        gt_paths.append(os.path.abspath(folder))
    log.debug('genthemall path is: \n%s' % '\n'.join(gt_paths))
    return gt_paths

def load_config(config_file = 'genthemall.cfg'):
    """Load config file convert to python object."""
    log.debug('Loading config file[%s]...', config_file)
    return Config(config_file)
