import logging, importlib, sys

log = logging.getLogger('genthemall.utils')

def load_class(clazz):
    """
    util method for dynamic load class.
    """
    dotIdx = clazz.rindex('.')
    mod = importlib.import_module(clazz[0:dotIdx])
    return getattr(mod, clazz[dotIdx+1:])

def load_function(fn):
    """
    util method for dynamic load function.
    """
    return load_class(fn)
        
def load_command(cmdName):
    """
    util method for dynamic load genthemall command.
    """
    return load_class('genthemall.commands.Command%s%s' % \
                          (cmdName[0].upper(), cmdName[1:]))

def transform_config(config, _type):
    """
    Transform config to some type config.
    """
    try:
        confFn = load_function('genthemall.conf.%s' % _type)
        confFn(config)
    except AttributeError:
        log.error('config type [%s] not found.' % (_type))
        sys.exit(1)
