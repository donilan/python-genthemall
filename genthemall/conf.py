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

def java(config):
    """
    Put the config into this method, and make it to java config.
    """
    config['package'] = '.'.join(config['namespace'].split('.')[::-1])
    config['path'] = config['package'].replace('.', '/')
    for m in config.get('modules', []):
        m.setdefault('camelName', _to_camel_name(m['name']))
        m.setdefault('pascalName', _to_pascal_name(m['name']))
        m.setdefault('displayName', _to_pascal_name(m['name']))
        for f in m.get('fields', []):
            f.setdefault('camelName', _to_camel_name(f['name']))
            f.setdefault('required', True)
            f.setdefault('pascalName', _to_pascal_name(f['name']))
            f.setdefault('getter', 'get%s' % f.get('pascalName'))
            f.setdefault('setter', 'set%s' % f.get('pascalName'))
            f.setdefault('formatSymbol', '%d' if f.get('type') in \
                         ['int', 'long'] else '%s')
            f.setdefault('javaType', java_type_map[f.get('type')])
            f.setdefault('javaShortType', java_short_type_map[f.get('type')])
            f.setdefault('min', default_min_map[f.get('type')])
            f.setdefault('max', default_max_map[f.get('type')])
            f.setdefault('isId', True if f['name'] == 'id' else False)
            f.setdefault('order', -1 if f['isId'] else 0)
            f.setdefault('editable', False if f['isId'] else True)
            f.setdefault('listable', False if f['isId'] else True)

        m.get('fields').sort(lambda a, b: a['order'] - b['order'])
    return config

def oracle(config):
    """
    Put the config into this method, and make it to oracle config.
    """
    for m in config.get('modules', []):
        m.setdefault('tableName', _to_upper_name(m['name']))
        m.setdefault('pascalName', _to_pascal_name(m['name']))
        m.setdefault('camelName', _to_camel_name(m['name']))
        for f in m.get('fields', []):
            f.setdefault('required', True)
            f.setdefault('columnName', _to_upper_name(f['name']))
            f.setdefault('databaseType', \
                         database_type_map[f.get('type', 'string')])
            f.setdefault('max', default_max_map[f.get('type', 'string')])
            f.setdefault('isId', True if f['name'] == 'id' else False)
            f.setdefault('order', -1 if f['isId'] else 0)

        m.get('fields').sort(lambda a, b: a['order'] - b['order'])        
    return config

