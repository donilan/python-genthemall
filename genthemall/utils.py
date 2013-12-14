import logging, importlib

log = logging.getLogger('genthemall.utils')

def load_class(clazz):
    log.debug('loading class [%s]...' % clazz)
    dotIdx = clazz.rindex('.')
    mod = importlib.import_module(clazz[0:dotIdx])
    return getattr(mod, clazz[dotIdx+1:])
        
def load_command(cmdName):
    return load_class('genthemall.commands.Command%s%s' % \
                          (cmdName[0].upper(), cmdName[1:]))
