
import os, os.path, yaml, logging, random, subprocess, hashlib, re, tempfile, json, time
from threading import Thread, Event
from queue import Queue, Empty

from .bus import bus
from . import alerts
from .config import config


_audioFileName = 'audio.yaml'

_logger = logging.getLogger('Audio')
_exitEvent = Event()
_thread = None
_audioConfig = None
_audioFile = os.path.join(config.getpath('audio', 'audioDir'), _audioFileName)

_lastModifiedTime = None
_playQueue = Queue()
_clips = {}


@bus.on('server/start')
def _bus_serverStart():
    global _thread
    _load()
    _exitEvent.clear()
    _thread = Thread(target = _threadLoop, name = 'AudioThread')
    _thread.daemon = True
    _thread.start()

@bus.on('server/stop')
def _bus_serverStop():
    _exitEvent.set()

@bus.on('config/loaded')
def _bus_configLoaded():
    global _audioFile
    ad = config.getpath('audio', 'audioDir')
    _audioFile = os.path.join(ad, _audioFileName)
    _load()
        
@bus.on('socket/consoleConnect')
def _bus_consoleConnect():
    bus.emit('audio/play', 'startup', console = True)

def _threadLoop():
    _logger.info('Audio thread started')
    try:
        while not _exitEvent.is_set():
            timeout = config.getfloat('audio', 'fileCheckInterval')
            try:
                item = _playQueue.get(block = True, timeout = timeout)
                _playClip(item)
            except Empty:
                _checkConfig()
    except Exception as e:
        _logger.exception(str(e))
    _logger.info('Audio thread stopped')
    alerts.add('Audio thread stopped!')

def _checkConfig():
    t = 0
    if os.path.isfile(_audioFile):
        t = os.path.getmtime(_audioFile)
    if t > _lastModifiedTime:
        _load()

def _playClip(item):
    clipName = item['clip']
    del(item['clip'])
    if not clipName in _clips:
        _logger.debug('No configured clips for {}'.format(clipName))
        return
    _logger.debug('Playing clip {}'.format(clipName))
    clip = _clips[clipName]
    r = random.random()
    for file in clip:
        if r < file[1]:
            bus.emit('audio/playFile', **{'file': file[0], **item})
            return
    _logger.warning('No file found for {}!'.format(clipName))
    
@bus.on('audio/play')
def _on_audioPlay(clip, console = False, sessionId = False, broadcast = False):
    if not console and not sessionId and not broadcast:
        _logger.warning('No destination for audio!')
        return
    _playQueue.put_nowait({
        'clip': clip,
        'console': console,
        'sessionId': sessionId,
        'broadcast': broadcast,
    })
    
def setVolume(volume):
    open(config.getpath('audio', 'volumeFile'), 'w').write(str(volume))
    bus.emit('audio/volume', volume)

def getVolume():
    try:
        return float(open(config.getpath('audio', 'volumeFile')).read().rstrip())
    except IOError:
        return 1
    
def _load():
    global _lastModifiedTime, _audioConfig, _clips
    
    _audioConfig = {}
    _lastModifiedTime = 0
    
    if os.path.isfile(_audioFile):
        try:
            with open(_audioFile) as f:
                _audioConfig = yaml.load(f)
            _lastModifiedTime = os.path.getmtime(_audioFile)
        except Error as e:
            _logger.error('Error while loading audio configuration: {}'.format(e))
            return

    if 'tts' not in _audioConfig or not isinstance(_audioConfig['tts'], dict):
        _audioConfig['tts'] = {}
    if 'effects' not in _audioConfig or not isinstance(_audioConfig['effects'], list):
        _audioConfig['effects'] = []
        
    _clips = {}
    
    for clipName in _audioConfig['clips'].keys():
    
        clipFiles = {}
        totalWeight = 0
        
        for clipConfig in _audioConfig['clips'][clipName]:
        
            clipConfig = _normalizeClipConfig(clipConfig)
            if clipConfig is None: continue
            
            file = _generateClipFileName(clipName, clipConfig)
            if file is None: continue
            
            #print('-------------------')
            #print('clipConfig: ' + str(clipConfig))
            #print('file: ' + file)
            
            if _isAudioFile(file):
                _logger.info('Found clip {} for {}'.format(file, clipName))
            else:
                _logger.debug('Generating clip {} for {}'.format(file, clipName))
                startTime = time.time()
                if not _generateClipFile(file, clipConfig):
                    continue
                _logger.info('Generated clip {} for {} in {:.2f} seconds'.format(file, clipName, time.time() - startTime))
                                
            weight = 1 if 'weight' not in clipConfig else float(clipConfig['weight'])
            totalWeight = totalWeight + weight
            clipFiles[file] = weight
                    
        # build weighted clip
        clip = []
        runningTotal = 0
        for (file, weight) in clipFiles.items():
            clip.append((file, runningTotal + (weight / totalWeight)))
            runningTotal = runningTotal + (weight / totalWeight)
        if clip:
            _clips[clipName] = clip

    if config.getboolean('audio', 'purgeClips'):
        for file in [f for f in os.listdir(config.getpath('audio', 'audioDir')) if _isAudioFile(f) and f.lower().endswith(('.mp3', '.wav', '.ogg'))]:
            purgeIt = True
            for (clipName, clips) in _clips.items():
                for clip in clips:
                    if file == clip[0]:
                        purgeIt = False
                        break
                if not purgeIt: break
            if purgeIt:
                _logger.info('Purged audio clip {}'.format(file))
                os.remove(os.path.join(config.getpath('audio', 'audioDir'), file))
            
    _logger.info('Audio clips loaded')
    bus.emit('audio/clipsLoaded')
        
def _isAudioFile(name):
    return os.path.isfile(os.path.join(config.getpath('audio', 'audioDir'), name))

def _normalizeClipConfig(clipConfig):

    if isinstance(clipConfig, str):
        if _isAudioFile(clipConfig):
            clipConfig = {
                'clip': clipConfig
            }
        else:
            clipConfig = {
                'text': clipConfig
            }
            
    elif not isinstance(clipConfig, dict):
        _logger.warning('Invalid clip configuration: {}'.format(clipConfig))
        return None

    if 'text' in clipConfig or 'ssml' in clipConfig:
        if 'text' in clipConfig:
            clipConfig['text'] = re.sub(r"(\r\n|\r|\n)", ' ', clipConfig['text'])
        elif 'ssml' in clipConfig:
            clipConfig['ssml'] = re.sub(r"(\r\n|\r|\n)", ' ', clipConfig['ssml'])
        if 'tts' not in clipConfig:
            clipConfig['tts'] = {**_audioConfig['tts']}
        else:
            clipConfig['tts'] = {**_audioConfig['tts'], **clipConfig['tts']}
        if 'effects' in clipConfig['tts']:
            if 'effects' in clipConfig:
                clipConfig['effects'] = clipConfig['effects'] + clipConfig['tts']['effects']
            else:
                clipConfig['effects'] = clipConfig['tts']['effects']
            del(clipConfig['tts']['effects'])
    
    effects = []
    if 'effects-pre' in clipConfig and isinstance(clipConfig['effects-pre'], list):
        effects = effects + clipConfig['effects-pre']
    
    if 'effects' in clipConfig and isinstance(clipConfig['effects'], list):
        effects = effects + clipConfig['effects']
    else:
        effects = effects + _audioConfig['effects']
        
    if 'effects-post' in clipConfig and isinstance(clipConfig['effects-post'], list):
        effects = effects + clipConfig['effects-post']
        
    clipConfig['effects'] = effects
    
    return clipConfig

def _generateClipFileName(clipName, clipConfig):
    hash = hashlib.md5()

    if 'clip' in clipConfig:
        if _isAudioFile(clipConfig['clip']):
            if clipConfig['effects']:
                hash.update(clipConfig['clip'].encode())
            else:
                return clipConfig['clip']
        else:
            _logger.warning('Clip file {} not found!'.format(clipConfig['clip']))
            return None
            
    elif 'text' in clipConfig or 'ssml' in clipConfig:
        if 'text' in clipConfig:
            hash.update(clipConfig['text'].encode())
        elif 'ssml' in clipConfig:
            hash.update(clipConfig['ssml'].encode())
        for k in sorted(clipConfig['tts'].keys()):
            if k == 'credentials': continue
            hash.update((k + str(clipConfig['tts'][k])).encode())
        
    for e in clipConfig['effects']:
        hash.update(e.encode())
            
    return '{}-{}.{}'.format(clipName, hash.hexdigest(), config.get('audio', 'clipFormat'))
    
def _generateClipFile(file, clipConfig):
    if 'clip' in clipConfig:
        srcFile = clipConfig['clip']
        deleteSource = False
        
    elif 'text' in clipConfig or 'ssml' in clipConfig:
        srcFile = _createTempFile(suffix = '.' + config.get('audio', 'clipFormat'))
        deleteSource = True
        if not _phraseToFile(clipConfig, srcFile):
            try:
                os.remove(srcFile)
            except:
                pass
            return False
    
    for effect in clipConfig['effects']:
        dstFile = _applyEffect(srcFile, effect)
        if not dstFile: return False
        if deleteSource:
            try:
                os.remove(srcFile)
            except:
                pass
            deleteSource = False
        srcFile = dstFile
        
    try:
        os.rename(srcFile, os.path.join(config.getpath('audio', 'audioDir'), file))
    except IOError as e:
        _logger.exception(e)
        return False
        
    return True
    
def _phraseToFile(clipConfig, file):
    
    cmd = os.path.join(config.getpath('server', 'binDir'), 'googleTTS.py')

    cfg = {
        'ttsConfig': clipConfig['tts'],
        'file': file,
    }
    if 'text' in clipConfig:
        cfg['text'] = clipConfig['text']
    elif 'ssml' in clipConfig:
        cfg['ssml'] = '<speak>' + clipConfig['ssml'] + '</speak>'
    
    _logger.debug('TTS config: {}'.format(cfg))
    
    if config.getboolean('audio', 'inProcessTTS'):
        try:
            tts(**cfg)
            return True
        except Exception as e:
            _logger.error(e)
            return False

    else:
        try:
            out = subprocess.run(cmd,
                input = json.dumps(cfg),
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                universal_newlines = True)
            if out.stdout:
                _logger.debug(out.stdout)
            if out.returncode != 0:
                _logger.error('Non-zero return status from TTS command "{}"!'.format(cmd))
                return False
            return True
        except IOError as e:
            _logger.error('Error from TTS command "{}"!'.format(cmd))
            _logger.error(e)
            return False
    
def _applyEffect(srcFile, cmd):
    dstFile = _createTempFile(suffix = '.' + config.get('audio', 'clipFormat'))
    cmd = cmd.replace('{i}', srcFile)
    cmd = cmd.replace('{o}', dstFile)
    try:
        out = subprocess.run(cmd,
            shell = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True)
        if out.stdout:
            _logger.debug(out.stdout)
        if out.returncode != 0:
            _logger.error('Non-zero return status from effect command "{}"!'.format(cmd))
            return False
        return dstFile
    except IOError as e:
        _logger.error('Error from effect command "{}"!'.format(cmd))
        _logger.error(e)
        return False
    
def _createTempFile(suffix = None):
    file = tempfile.NamedTemporaryFile(delete = False, suffix = suffix)
    return file.name

def tts(ttsConfig, file, text = None, ssml = None, ):
    _logger.debug('Performing TTS {}'.format(file))
    try:
        from google.cloud import texttospeech
        if 'credentials' not in ttsConfig:
            raise ValueError('Missing TTS credentials!')
            
        credsFile = ttsConfig['credentials']
        credsFile = os.path.expanduser(credsFile)
        if not os.path.isabs(credsFile):
            credsFile = os.path.normpath(os.path.join(config.getpath('audio', 'audioDir'), credsFile))
            
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credsFile
        client = texttospeech.TextToSpeechClient()
        
        if ssml:
            input = texttospeech.types.SynthesisInput(ssml = ssml)
        elif text:
            input = texttospeech.types.SynthesisInput(text = text)
        else:
            raise ValueError('One of ssml or text argument must be supplied!')
        
        args = {k[6:]:v for k,v in ttsConfig.items() if k[:6] == 'voice.'}
        voice = texttospeech.types.VoiceSelectionParams(**args)
        
        args = {k[6:]:v for k,v in ttsConfig.items() if k[:6] == 'audio.'}
        fmt = config.get('audio', 'clipFormat')
        if fmt == 'mp3':
            args['audio_encoding'] = texttospeech.enums.AudioEncoding.MP3
        elif fmt == 'ogg':
            args['audio_encoding'] = texttospeech.enums.AudioEncoding.OGG_OPUS
        elif fmt == 'wav':
            args['audio_encoding'] = texttospeech.enums.AudioEncoding.LINEAR16
        else:
            raise ValueError('Unsupported clip format {}!'.format(fmt))
            
        audio = texttospeech.types.AudioConfig(**args)
        
        response = client.synthesize_speech(input, voice, audio)
        with open(file, 'wb') as f:
            f.write(response.audio_content)
        _logger.debug('TTS saved to {}'.format(file))
    except Exception as e:
        _logger.error(e)
        raise e
    