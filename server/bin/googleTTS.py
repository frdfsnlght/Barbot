#!/usr/bin/python3

import sys, os, logging, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import barbot.config

config = barbot.config.load()

import barbot.logging

barbot.logging.configure()

import barbot.audio

for line in sys.stdin:
    cfg = json.loads(line)
    barbot.audio.tts(**cfg)

