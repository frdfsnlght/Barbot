
import sys, os, time, logging, subprocess, re, time
from threading import Thread, Event

from .config import config
from .bus import bus


_wpaSupplicantNetworkBeginPattern    = re.compile(r"\s*network\s*=\s*\{")
_wpaSupplicantNetworkEndPattern      = re.compile(r"\s*\}")
_wpaSupplicantNetworkSSIDPattern     = re.compile(r"\s*ssid\s*=\s*\"(.+)\"")
_wpaSupplicantNetworkPSKPattern      = re.compile(r"\s*psk\s*=\s*\"(.+)\"")
_wpaSupplicantNetworkPriorityPattern = re.compile(r"\s*priority\s*=\s*(\d+)")

_wifiStatePattern = re.compile(r"(?i)(?s)SSID:\"([^\"]+)\".*Link Quality=(\d+)/(\d+).*Signal level=(\-?\d+)")
_wifiNetworkCellPattern = re.compile(r"(?i)(?s)Quality=(\d+)/(\d+).*Signal level=(\-?\d+).*SSID:\"([^\"]+)\".*Authentication Suites.*?: ([\w ]+)")


state = False
_logger = logging.getLogger('Wifi')
_exitEvent = Event()
_thread = None
_scannedNetworks = []
_wpaSupplicantHeader = []
_wpaSupplicantNetworks = []


@bus.on('server/stop')
def _bus_serverStop():
    _exitEvent.set()
    
@bus.on('server/start')
def _startThread():
    global _thread, state
    _exitEvent.clear()
    if not config.getint('wifi', 'checkInterval'):
        logging.info('Wifi checking disabled')
        return
    state = _getState()
    if not state:
        logging.info('Wifi not available')
        return
    
    _thread = Thread(target = _threadLoop, name = 'WifiThread')
    _thread.daemon = True
    _thread.start()

def _threadLoop():
    _logger.info('Wifi thread started')
    while not _exitEvent.is_set():
        _updateState()
        _readWPASupplicant(config.getpath('wifi', 'wpaSupplicantFile'))
        _exitEvent.wait(config.getint('wifi', 'checkInterval'))
            
    _logger.info('Wifi thread stopped')
    
def _readWPASupplicant(path):
    global _wpaSupplicantHeader, _wpaSupplicantNetworks
    _wpaSupplicantHeader = []
    _wpaSupplicantNetworks = []
    try:
        with open(path) as f:
            content = [line.rstrip() for line in f.readlines()]
        network = False
        for line in content:
            if type(network) is dict:
                m = _wpaSupplicantNetworkEndPattern.match(line)
                if m:
                    _wpaSupplicantNetworks.append(network)
                    network = False
                    continue
                m = _wpaSupplicantNetworkSSIDPattern.match(line)
                if m:
                    network['ssid'] = m.group(1)
                m = _wpaSupplicantNetworkPSKPattern.match(line)
                if m:
                    network['secured'] = True
                m = _wpaSupplicantNetworkPriorityPattern.match(line)
                if m:
                    network['priority'] = int(m.group(1))
                    continue
                    
                network['content'].append(line)
            elif _wpaSupplicantNetworkBeginPattern.match(line):
                network = {
                    'ssid': None,
                    'secured': False,
                    'priority': 0,
                    'content': []
                }
            elif line:
                _wpaSupplicantHeader.append(line)
    except FileNotFoundError:
        pass
    
def _writeWPASupplicant(path):
    try:
        with open(path, 'w') as f:
            for line in _wpaSupplicantHeader:
                f.write(line + '\n')
            for network in _wpaSupplicantNetworks:
                f.write('network={\n')
                for line in network['content']:
                    f.write(line + '\n')
                f.write('  priority={}\n'.format(network['priority']))
                f.write('}\n')
        return True
    except IOError as e:
        _logger.error(e)
        return False
    
def _setDefaultWPASupplicantPriorities():
    for network in _wpaSupplicantNetworks:
        network['priority'] = 0
        
def _getSavedNetwork(ssid):
    for network in _wpaSupplicantNetworks:
        if network['ssid'] == ssid:
            return network
    return None
    
def _getScannedNetwork(ssid):
    for network in _scannedNetworks:
        if network['ssid'] == ssid:
            return network
    return None
    
def _updateState():
    global state
    s = _getState()
    update = False

    if (s and not state) or (not s and state):
        update = True
    elif s and state:
        for k in ('ssid', 'quality', 'signal', 'bars'):
            if (k in s and k not in state) or (k not in s and k in state):
                update = True
            elif k in s and k in state:
                update = s[k] != state[k]
            if update:
                break
    
    if update:
        state = s
        bus.emit('wifi/state', state)
    
def _getState():
    try:
        out = subprocess.run(['iwconfig', config.get('wifi', 'interface')],
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
    except IOError as e:
        _logger.error(e)
        return False
    if out.returncode != 0:
        # interface not found 
        return False
    m = _wifiStatePattern.search(out.stdout)
    if not m:
        # not connected
        return {
            'ssid': False,
        }
    # connected
    state = {
        'ssid': m.group(1),
        'quality': m.group(2) + '/' + m.group(3),
        'signal': int(m.group(4)),
        'bars': int(4.9 * float(m.group(2)) / float(m.group(3))),
        'connected': True
    }
    return state

def _scanNetworks():
    networks = []
    
    try:
        scanned = False
        while not scanned:
            out = subprocess.run(['sudo', 'iwlist', config.get('wifi', 'interface'), 'scan'], stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
            if out.returncode == 0:
                for cell in re.split(r"Cell ", out.stdout):
                    m = _wifiNetworkCellPattern.search(cell)
                    if m:
                        network = {
                            'ssid': m.group(4).replace('\\x00', ''),
                            'quality': m.group(1) + '/' + m.group(2),
                            'signal': int(m.group(3)),
                            'auth': m.group(5).split(' '),
                            'bars': int(4.9 * float(m.group(1)) / float(m.group(2))),
                            'scanned': True,
                        }
                        network['secured'] = len(network['auth']) > 0
                        if network['ssid']:
                            networks.append(network)
                scanned = True
            elif not re.search('(?i)Device or resource busy|Resource temporarily unavailable', out.stdout):
                _logger.error('Got return status of {} while scanning for wifi networks: {}'.format(out.returncode, out.stdout.strip()))
                scanned = True
    except IOError as e:
        _logger.error(e)
        
    return networks

def getNetworks():
    global _scannedNetworks
    
    _scannedNetworks = _scanNetworks()
    
    networks = {}
    
    # start with saved networks
    for n in _wpaSupplicantNetworks:
        network = {
            'ssid': n['ssid'],
            'saved': True,
            'secured': n['secured'],
        }
        networks[network['ssid']] = network
    
    # merge in scanned networks
    for network in _scannedNetworks:
        if network['ssid'] in networks:
            networks[network['ssid']] = {**network, **networks[network['ssid']]}
        else:
            networks[network['ssid']] = {**network}

    # merge in connected network
    if state and state['ssid']:
        if state['ssid'] in networks:
            networks[state['ssid']] = {**state, **networks[state['ssid']]}
        else:
            networks[state['ssid']] = {**state}
    
    return list(networks.values())
    
def connectToNetwork(params):
    global state
    network = _getSavedNetwork(params['ssid'])
    if network:
        _wpaSupplicantNetworks.remove(network)
    else:
        network = {
            'ssid': params['ssid'],
            'content': [
                '  ssid="{}"'.format(params['ssid']),
            ]
        }
        if 'password' in params:
            network['content'].append('  psk="{}"'.format(params['password']))
            network['secured'] = True
        else:
            network['content'].append('  key_mgmt=NONE')
            network['secured'] = False
        
        if not _getScannedNetwork(params['ssid']):
            network['content'].append('  scan_ssid=1')
            
        _logger.info('Saved wifi network "{}"'.format(network['ssid']))

    # crank down all the other network priorities
    _setDefaultWPASupplicantPriorities()
    
    # add desired network to the head of the list and set a higher priority
    network['priority'] = 1
    _wpaSupplicantNetworks[:0] = [network]
    
    if _writeWPASupplicant(config.getpath('wifi', 'wpaSupplicantFile')):
        try:
            out = subprocess.run(['wpa_cli', '-i', config.get('wifi', 'interface'), 'reconfigure'], stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
            if out.returncode != 0:
                _logger.error('Got return status of {} while trying to wpa_cli reconfigure for network: {}'.format(out.returncode, out.stdout.strip()))
                return
            _logger.info('Reconfigured wifi for network "{}"'.format(network['ssid']))
            
            out = subprocess.run(['wpa_cli', '-i', config.get('wifi', 'interface'), 'reassociate'], stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
            if out.returncode != 0:
                _logger.error('Got return status of {} while trying to wpa_cli reassociate for network: {}'.format(out.returncode, out.stdout.strip()))
                return
            
            _logger.info('Reassociated wifi for network "{}"'.format(network['ssid']))
        except IOError as e:
            _logger.error(e)
        _updateState()

def disconnectFromNetwork(ssid):
    global state
    if state and state['ssid'] == ssid:
        try:
            out = subprocess.run(['wpa_cli', '-i', config.get('wifi', 'interface'), 'disconnect'], stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
            if out.returncode != 0:
                _logger.error('Got return status of {} while trying to disconnect from wifi network: {}'.format(out.returncode, out.stdout.strip()))
            _logger.info('Disconnected from wifi network "{}"'.format(ssid))
        except IOError as e:
            _logger.error(e)
        _updateState()

def forgetNetwork(ssid):
    disconnectFromNetwork(ssid)
    network = _getSavedNetwork(ssid)
    if network:
        _wpaSupplicantNetworks.remove(network)
        _writeWPASupplicant(config.getpath('wifi', 'wpaSupplicantFile'))
        _logger.info('Removed saved wifi network "{}"'.format(ssid))

    