
import os, configparser, logging, time, re

from .bus import bus
from .config import config


_booleanPattern = re.compile(r"(i?)(true|false|yes|no)")
_intPattern = re.compile(r"-?\d+$")
_floatPattern = re.compile(r"-?\d*\.\d+$")

_logger = logging.getLogger('Settings')
_settings = None
_lastSettingsCheckTime = 0
_lastSettingsModifiedTime = None


@bus.on('server/start')
def _bus_serverStart():
    global _settings
    _settings = configparser.ConfigParser(
        interpolation = None,
    )
    _settings.optionxform = str    # preserve option case
    _load()
    
@bus.on('server/tick')
def _bus_serverTick():
    global _lastSettingsCheckTime
    if (time.time() - _lastSettingsCheckTime) > config.getfloat('settings', 'settingsCheckInterval'):
        _lastSettingsCheckTime = time.time()
        file = config.getpath('settings', 'settingsFile')
        if os.path.isfile(file) and os.path.getmtime(file) > _lastSettingsModifiedTime:
            _load()

@bus.on('config/loaded')
def _load():
    global _lastSettingsModifiedTime
    file = config.getpath('settings', 'settingsFile')
    _settings.clear()
    if os.path.isfile(file):
        _lastSettingsModifiedTime = os.stat(file).st_mtime
        _settings.read(file)
    _logger.info('Settings loaded')
    bus.emit('settings/loaded')
    
def export():
    all = dict(config.items('settings'))
    if 'settingsFile' in all: del all['settingsFile']
    if 'settingsCheckInterval' in all: del all['settingsCheckInterval']
    for k, v in all.items():
        if _booleanPattern.match(v):
            all[k] = getboolean(k)
        elif _intPattern.match(v):
            all[k] = getint(k)
        elif _floatPattern.match(v):
            all[k] = getfloat(k)
        else:
            all[k] = get(k)
    return all

def get(key):
    return _settings.get('DEFAULT', key, fallback = config.get('settings', key))

def getint(key):
    return _settings.getint('DEFAULT', key, fallback = config.getint('settings', key))

def getfloat(key):
    return _settings.getfloat('DEFAULT', key, fallback = config.getfloat('settings', key))

def getboolean(key):
    return _settings.getboolean('DEFAULT', key, fallback = config.getboolean('settings', key))

def set(key, value):
    global _lastSettingsModifiedTime
    defaultValue = config.get('settings', key)
    
    if _booleanPattern.match(defaultValue):
        if not isinstance(value, bool):
            raise ValueError('value of {} must be a boolean'.format(key))
        defaultValue = config.getboolean('settings', key)
        
    elif _intPattern.match(defaultValue):
        if not isinstance(value, int):
            raise ValueError('value of {} must be an integer'.format(key))
        defaultValue = config.getint('settings', key)
            
    elif _floatPattern.match(defaultValue):
        if not isinstance(value, (float, int)):
            raise ValueError('value of {} must be a float'.format(key))
        defaultValue = config.getfloat('settings', key)

    if value == defaultValue and _settings.has_option('DEFAULT', key):
        _settings.remove_option('DEFAULT', key)
    else:
        _settings.set('DEFAULT', key, str(value))
    
    with open(config.getpath('settings', 'settingsFile'), 'w') as file:
        _settings.write(file)
    _lastSettingsModifiedTime = time.time()
    bus.emit('settings/changed')
