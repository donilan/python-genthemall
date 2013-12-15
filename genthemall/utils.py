import logging, importlib

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
