
from .bus import bus
from .config import config

default = ''
order = []
conversions = {}


@bus.on('server/start1')
def _bus_serverStart():
    load()

@bus.on('config/loaded')
def _bus_configLoaded():
    load()

def load():
    global default, order, conversions
    for (k, v) in config['units'].items():
        if k == 'default':
            default = v
        elif k == 'order':
            order = v.split(',')
        else:
            v = v.split(',')
            conversions[k] = {
                'label': k,
                'toML': float(v[0]),
                'precision': int(v[1])
            }

def toML(otherAmount, otherUnits):
    if otherUnits not in conversions:
        raise ValueError('Invalid units: {}'.format(otherUnits))
    return otherAmount * conversions[otherUnits]['toML']

def toOther(mlAmount, otherUnits):
    if otherUnits not in conversions:
        raise ValueError('Invalid units: {}'.format(otherUnits))
    return mlAmount / conversions[otherUnits]['toML']
    
def format(otherAmount, otherUnits, appendUnits = True):
    if otherUnits not in conversions:
        raise ValueError('Invalid units: {}'.format(otherUnits))
    str = format(otherAmount, '.{}f'.format(conversions[otherUnits]['precision']))
    if appendUnits:
        str = str + ' ' + otherUnits
    return str

def export():
    return {
        'default': default,
        'order': order,
        'conversions': conversions,
    }
