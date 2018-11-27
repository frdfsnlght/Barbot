#!/usr/bin/python3

import sys, os, time, argparse, serial, re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import barbot.config

config = barbot.config.load()

args = None
port = None
pumps = []
pumpSpeed = 12000
pumpAccel = 7500
loopDelta = 0.25
pumpDir = 0
pumpsFlushing = False
glassReady = False


class Pump():
    def __init__(self, id):
        self.id = id
        self.running = False
        self.stopped = False
        self.target = 0
        self.position = 0
        self.speed = 0
        self.acceleration = 0
    def __str__(self):
        return '[id={},running={},target={},position={},speed={},accel={}]'.format(
            self.id,
            self.running,
            self.target,
            self.position,
            self.speed,
            self.acceleration)
    
    
def run():
    global port
    
    port = serial.Serial(args.port, config.getint('serial', 'speed'), timeout = loopDelta)
    print('Serial port {} opened at {}'.format(port.name, port.baudrate))

    for id in range(0, config.getint('pumps', 'count')):
        pumps.append(Pump(id))
    
    buffer = ''
    while True:
        try:
            ch = port.read()
            if ch:
                ch = ch.decode('ascii')
                if ch == '\r' or ch == '\n':
                    if buffer:
                        processCommand(buffer)
                        buffer = ''
                else:
                    buffer = buffer + ch
            loopPumps()
            loopSensors()
        except KeyboardInterrupt:
            break
        
def loopPumps():
    global pumpDir, pumpsFlushing
    # simulated pumps run at a constant speed and start/stop instantly
    running = False
    for pump in [p for p in pumps if p.running]:
        if pump.stopped:
            pump.running = False
            sendPumpStopped(pump)
        else:
            pump.position = pump.position + int(pump.speed * loopDelta * pumpDir)
            if (pump.target < 0 and pump.position <= pump.target) or (pump.target > 0 and pump.position >= pump.target):
                pump.position = pump.target
                pump.running = False
                sendPumpStopped(pump)
            else:
                running = True
    if not running:
        pumpDir = 0
        pumpsFlushing = False
        
def loopSensors():
    global glassReady
    newGlassReady = os.path.isfile(os.path.join(os.path.dirname(__file__), '..', 'var', 'glass'))
    if newGlassReady != glassReady:
        glassReady = newGlassReady
        send('*S{}{}'.format(0, 1 if glassReady else 0))

def processCommand(cmd):
    print('<- {}'.format(cmd))
    
    m = re.match(r"[A-Z].*\~([0-9A-F]{2})", cmd)
    if m:
        sentCS = int(m.group(1), 16)
        cmd = cmd[:-3]
        cs = 0
        for c in cmd.encode('ascii'):
            cs = cs ^ c
        if cs != sentCS:
            sendError('CHK')
            return

    ch = cmd[0].upper()
    
    if ch == 'P':
        processPumpCommand(cmd[1:])
    elif ch == 'C':
        processCommCommand(cmd[1:])
    elif ch == 'L':
        processLightsCommand(cmd[1:])
    elif ch == 'R':
        processPowerCommand(cmd[1:])
        
    else:
        sendError('invalid command')
    
def processPumpCommand(cmd):
    ch = cmd[0].upper()
    if ch == 'P':
        cmdPumpPump(cmd[1:])
    elif ch == 'H':
        cmdPumpHalt(cmd[1:])
    elif ch == 'F':
        cmdPumpFlush(cmd[1:])
    else:
        sendError('invalid pump command')
    
# <#>,<[-]steps>,<speed>,<accel>
def cmdPumpPump(cmd):
    global pumpDir
    
    if pumpsFlushing:
        sendError('pumps are flushing')
        return
    
    (id, cmd) = readUInt(cmd)
    (junk, cmd) = readDelim(cmd)
    if id >= len(pumps):
        sendError('invalid pump')
        return
    if pumps[id].running:
        sendError('pump is running')
        return
        
    (steps, cmd) = readInt(cmd)
    (junk, cmd) = readDelim(cmd)
    if steps == 0:
        sendError('invalid steps')
        return
    dir = -1 if steps < 0 else 1
    
    if pumpDir != 0 and dir != pumpDir:
        sendError('invalid direction')
        return
    
    (speed, cmd) = readUInt(cmd)
    (junk, cmd) = readDelim(cmd)
    if speed == 0:
        speed = pumpSpeed
    
    (accel, cmd) = readUInt(cmd)
    (junk, cmd) = readDelim(cmd)
    if accel == 0:
        accel = pumpAccel

    pump = pumps[id]
    pump.position = 0
    if abs(steps) > 1:
        pump.target = steps
    else:
        pump.target = 0
    pump.speed = speed
    pump.accel = accel
    pump.running = True
    pump.stopped = False
    pumpDir = dir
    
    sendOK()
    sendPumpRunning(pump)
    
# <#>    
def cmdPumpHalt(cmd):

    if pumpsFlushing:
        sendError('pumps are flushing')
        return

    (id, cmd) = readUInt(cmd)
    if id >= len(pumps):
        sendError('invalid pump')
        return
    if pumps[id].running:
        pumps[id].stopped = True
    sendOK()

# <#>,<#>,...
def cmdPumpFlush(cmd):
    global pumpsFlushing
    
    if not cmd:
        # stop flushing
        if pumpsFlushing:
            for pump in [p for p in pumps if p.running]:
                pump.stopped = True
        sendOK()
            
    else:
        # start flushing
        if pumpsFlushing:
            sendError('pumps are already flushing')
            return
            
        if pumpsAreRunning():
            sendError('pumps are running')
            return
        
        for i in range(0, config.getint('pumps', 'count')):
            (id, cmd) = readUInt(cmd)
            if id >= len(pumps):
                sendError('invalid pump')
                return
            pump = pumps[id]
            pump.position = 0
            pump.target = 0
            pump.speed = pumpSpeed
            pump.acceleration = pumpAccel
            pump.running = True
            pump.stopped = False
            sendPumpRunning(pump)
            
            (delim, cmd) = readDelim(cmd)
            if not delim:
                break;
        
        pumpsFlushing = True
        sendOK()
    
def processCommCommand(cmd):
    sendOK()
    
def processLightsCommand(cmd):
    sendOK()
    
def processPowerCommand(cmd):
    sendOK()
    
    
    
def readInt(str):
    neg = False
    i = 0
    if str[0] == '-':
        str = str[1:]
        neg = True
    while str and str[0].isdigit():
        i = (i * 10) + (ord(str[0]) - ord('0'))
        str = str[1:]
    return (-i if neg else i, str)

def readUInt(str):
    i = 0
    while str and str[0].isdigit():
        i = (i * 10) + (ord(str[0]) - ord('0'))
        str = str[1:]
    return (i, str)

def readDelim(str, delim = ','):
    if str and str[0] == delim:
        str = str[1:]
        return (True, str)
    else:
        return (False, str)
    
    
    
    
def send(str):
    port.write((str + '\n').encode('ascii'))
    print('-> {}'.format(str))
    
def sendError(str):
    send('!' + str)

def sendMessage(str):
    send('#' + str)
    
def sendOK():
    send('OK')
    
def sendEvent(str):
    send('*' + str)
    
def sendPumpRunning(pump):
    send('*PR{}'.format(pump.id))

def sendPumpStopped(pump):
    send('*PS{},{}'.format(pump.id, pump.position))

def pumpsAreRunning():
    for pump in pumps:
        if pump.running:
            return True
    return False
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Barbot Hardware Simulator')
    parser.add_argument('port', help = 'the serial port to connect to')
    args = parser.parse_args()
    run()
        





