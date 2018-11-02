
import logging

from .bus import bus


_alerts = []


def add(msg):
    _alerts.append(msg)
    bus.emit('alerts/add')
    
def clear():
    _alerts.clear()
    bus.emit('alerts/clear')
    
def getAll():
    return _alerts
    