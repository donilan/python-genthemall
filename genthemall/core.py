import logging
from config import Config

log = logging.getLogger('genthemall.core')

def generate(config_file):
    pass

def find_templates(folder = './'):
    """Load template files from sepecify folder."""
    pass

def load_config(config_file = 'genthemall.cfg'):
    """Load config file convert to python object."""
    log.debug('Loading config file[%s]...', config_file)
    return Config(config_file)
