import logging, os
from config import Config

log = logging.getLogger('genthemall.core')

def generate(config_file, folder = None):
    template_files = find_template_files(folder)

    print template_files

def find_template_files(folder = None):
    """Find template files from sepecify folder."""
    folders = find_template_folders(folder)
    _files = []
    for _folder in folders:
        for root, dirs, files in os.walk(_folder):
            for file in files:
                if file.endswith(".gt"):
                    _files.append(os.path.join(root, file))
    log.debug('Found [%d ] template files.%s' % len_files)
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
