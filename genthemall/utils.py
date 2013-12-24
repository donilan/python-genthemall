import logging, importlib, sys, os

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


def copyfile(source, dest, buffer_size=1024*1024):
    """
    Copy a file from source to dest. source and dest
    can either be strings or any object with a read or
    write method, like StringIO for example.
    """
    if not hasattr(source, 'read'):
        source = open(source, 'rb')
    if not hasattr(dest, 'write'):
        dest = open(dest, 'wb')

    while 1:
        copy_buffer = source.read(buffer_size)
        if copy_buffer:
            dest.write(copy_buffer)
        else:
            break

    source.close()
    dest.close()

def copyfiles(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                copyfiles(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        copyfile(src, dest)
            
