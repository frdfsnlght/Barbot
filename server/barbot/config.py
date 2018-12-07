
import os, configparser, logging, time

from .bus import bus


_logger = logging.getLogger('Config')
config = None
_lastConfigCheckTime = 0
_lastConfigModifiedTime = None
_rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_defaultConfig = os.path.join(_rootDir, 'etc', 'config-default.ini')
_localConfig = os.path.join(_rootDir, 'etc', 'config.ini')


@bus.on('server/tick')
def _bus_serverTick():
    global _lastConfigCheckTime
    if (time.time() - _lastConfigCheckTime) > config.getfloat('server', 'configCheckInterval'):
        _lastConfigCheckTime = time.time()
        if max(os.path.getmtime(_defaultConfig), os.path.getmtime(_localConfig)) > _lastConfigModifiedTime:
            _load()

def load():
    global config
    config = configparser.ConfigParser(
        interpolation = None,
        converters = {
            'path': _resolvePath
        }
    )
    config.optionxform = str    # preserve option case
    _load()
    return config

def _load():
    global _lastConfigModifiedTime
    _lastConfigModifiedTime = max(os.stat(_defaultConfig).st_mtime, os.stat(_localConfig).st_mtime)
    config.clear()
    config.read(_defaultConfig)
    config.read(_localConfig)
    _logger.info('Configuration loaded')
    bus.emit('config/loaded')

def _resolvePath(str):
    str = os.path.expanduser(str)
    if os.path.isabs(str):
        return str
    else:
        return os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), str))
