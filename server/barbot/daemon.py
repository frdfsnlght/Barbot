
import os, sys, atexit, signal, time, errno, psutil

from .config import config


def _daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError as e:
        sys.stderr.write('fork #1 failed: {} ({})\n'.format(e.errno, e.strerror))
        sys.exit(1)

    # decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as e:
        sys.stderr.write('fork #2 failed: {} ({})\n'.format(e.errno, e.strerror))
        sys.exit(1)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open('/dev/null', 'r')
    so = open('/dev/null', 'a+')
    se = open('/dev/null', 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # write pidfile
    atexit.register(_deletePID)
    pid = str(os.getpid())
    open(getPIDFile(), 'w+').write('{}\n'.format(pid))

def _deletePID():
    os.remove(getPIDFile())
    
def _isSameProcessName(pid):
    p1 = psutil.Process()
    p2 = psutil.Process(pid)
    if p1.name() == p2.name(): return True
    if p1.cmdline()[1] == p2.cmdline()[1]: return True
    if os.path.basename(p1.cmdline()[1]) == os.path.basename(p2.cmdline()[1]): return True
    return False
    
def start(main):
    pid = getDaemonPID()
    if pid:
        try:
            os.kill(pid, 0)
            # process with pid is running, check if it's ours
            if _isSameProcessName(pid):
                sys.stderr.write('pidfile {} already exists\n'.format(getPIDFile()))
                sys.exit(1)
            else:
                sys.stderr.write('pidfile {} already exists but specified process is not ours\n'.format(getPIDFile()))
        except OSError as err:
            if err.errno == errno.ESRCH:    # no such process
                sys.stderr.write('pidfile {} already exists but no running process was found\n'.format(getPIDFile()))
            else:
                print(err)
                sys.exit(1)
                
    # Start the daemon
    _daemonize()
    main()

def stop():
    pid = getDaemonPID()
    if not pid:
        sys.stderr.write('pidfile {} does not exist\n'.format(getPIDFile()))
        return # not an error in a restart

    try:
        os.kill(pid, 0)
        # process with pid is running, check if it's ours
        if _isSameProcessName(pid):
            try:
                while 1:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
            except OSError as err:
                if err.errno == errno.ESRCH:    # no such process, must have exited
                    if os.path.exists(getPIDFile()):
                        os.remove(getPIDFile())
                else:
                    print(err)
                    sys.exit(1)
        else:
            sys.stderr.write('pidfile {} exists but specified process is not ours\n'.format(getPIDFile()))
            os.remove(getPIDFile())
            sys.exit(1)
    except OSError as err:
        if err.errno == errno.ESRCH:    # no such process
            sys.stderr.write('pidfile {} exists but specified process is not running\n'.format(getPIDFile()))
            os.remove(getPIDFile())
        else:
            print(err)
            sys.exit(1)

def restart(main):
    stop()
    start(main)

def status():
    pid = getDaemonPID()
    if pid:
        try:
            os.kill(pid, 0)
            # process with pid is running, check if it's ours
            if _isSameProcessName(pid):
                sys.stdout.write('Daemon is running with PID {}.\n'.format(pid))
            else:
                sys.stderr.write('pidfile {} exists but specified process is not ours\n'.format(getPIDFile()))
                sys.exit(1)
        except OSError as err:
            if err.errno == errno.ESRCH:    # no such process
                sys.stderr.write('pidfile {} exists but specified process is not running\n'.format(getPIDFile()))
            else:
                print(err)
                sys.exit(1)
    else:
        sys.stdout.write('Daemon is not running.\n')
    
def getDaemonPID():
    try:
        pf = open(getPIDFile(), 'r')
        pid = int(pf.read().strip())
        pf.close()
    except IOError:
        pid = None
    return pid
    
def getPIDFile():
    return config.getpath('server', 'pidFile')
