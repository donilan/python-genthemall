import logging, importlib

log = logging.getLogger('genthemall.utils')

def load_class(clazz):
    dotIdx = clazz.rindex('.')
    mod = importlib.import_module(clazz[0:dotIdx])
    return getattr(mod, clazz[dotIdx+1:])

def load_function(fn):
    return load_class(fn)
        
def load_command(cmdName):
    return load_class('genthemall.commands.Command%s%s' % \
                          (cmdName[0].upper(), cmdName[1:]))
