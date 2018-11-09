#!/usr/bin/python3

import sys, os, logging, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import barbot.config

config = barbot.config.load()

import barbot.logging

barbot.logging.configure()

import barbot.audio

cfg = json.loads(sys.stdin.read())
try:
    barbot.audio.tts(**cfg)
except Exception as e:
    print(e)
    sys.exit(1)

