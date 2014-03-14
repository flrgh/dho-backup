import os
from ConfigParser import SafeConfigParser

def parse_config(conf_file):
    '''Returns a dict with all global config data'''

    defaults = {
        'log_level'      : 'INFO',
        'max_logs'       : '5',
        'skip_filetypes' : '',
        'exclude'        : [], 
    }
    parser = SafeConfigParser(defaults=defaults)
    parser.read(conf_file)
    conf = {}
    conf['dho_access_key'] = parser.get('settings', 'access_key', raw=True)
    conf['dho_secret_key'] = parser.get('settings', 'secret_key', raw=True)
    conf['passphrase']     = parser.get('settings', 'passphrase', raw=True)
    conf['log_level']      = parser.get('settings', 'log_level')
    conf['log_file']       = parser.get('settings', 'log_file')
    conf['max_logs']       = parser.getint('settings', 'max_logs')
    conf['backup_zones']   = []

    for section in parser.sections():
        if section != 'settings':
            conf['backup_zones'].append(
                {
                    'directory'      : parser.get(section, 'directory'),
                    'bucket'         : parser.get(section, 'bucket'),
                    'encrypt'        : parser.getboolean(section, 'encrypt'), 
                    'exclude'        : map(parse_excludes, (ex.strip() for ex in parser.get(section, 'exclude').split(','))),
                }
            )

    return conf


def parse_excludes(exclusion):
    if os.path.isdir(exclusion):
        return exclusion.rstrip('/') + '/*'
    else:
        return exclusion
