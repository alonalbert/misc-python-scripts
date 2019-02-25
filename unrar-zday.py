#!/usr/local/bin/python3
#

import os
import re
import shutil
import datetime
import sys
from pathlib import Path
import requests
import configparser

from subprocess import call

def get_pushover_config_filename():
  home_dir = os.path.expanduser('~/.pushover')
  return home_dir if os.path.exists(home_dir) else os.path.dirname(os.path.realpath(__file__)) + '/.pushover'

def getRarFile(path):
  if os.path.isfile(path) and path.endswith(".rar"):
    return path

  files = os.listdir(path)
  for file in files:
    if file.endswith(".rar"):
      return os.path.join(path, file)

def handleZDay(outDir, path):
  rarFile = None
  files = os.listdir(path)
  for file in files:
    if file.endswith(".rar"):
      rarFile = os.path.join(path, file)

  if rarFile is None:
    print('not an archive')
    return

  name = os.path.basename(path)
  match = re.search(r"^(?P<series>[^.]*).((?P<episode>(\d\d.\d\d.\d\d)|(E\d+)).)?(?P<title>.*).XXX.*", name, re.IGNORECASE)

  if not match:
    print("ZDAY: Can't match %s" % name)
    return

  series =  re.sub(r"(([0-9]+)|([A-Z][a-z]*))", r"\1 ", match.group('series')).strip()
  episode = match.group('episode')
  if episode:
    episode = episode.replace(".", "-")
  else:
    episode = datetime.datetime.now().strftime('%Y-%m-%d')

  title = match.group('title').replace(".", " ").replace(' JAPANESE', '')

  dir = "%s/%s" % (outDir, series)
  tmpDir = "%s/tmp" % (dir)
  Path(tmpDir).mkdir(parents=True)

  print("Extracting %s" % rarFile)
  call(["unrar", "-o-", "-inul", "x", rarFile], cwd=tmpDir)

  for videoFile in os.listdir(tmpDir):
    src = "%s/%s" % (tmpDir, videoFile)
    dest = "%s/%s %s%s" % (dir, episode, title, os.path.splitext(videoFile)[1])
    shutil.move(src, dest)

  shutil.rmtree(tmpDir)
  message = '%s - %s' % (series, title)
  deluge_config = configparser.ConfigParser()
  deluge_config.read(get_pushover_config_filename())
  deluge_setup = deluge_config["setup"]
  requests.post('https://api.pushover.net/1/messages.json',
                data={
                  'user': deluge_setup['user'],
                  'token': deluge_setup['deluge-token'],
                  'sound': 'magic',
                  'message': message
                })

if __name__ == '__main__':
  dir = sys.argv[3]
  if dir == '/volume1/video/deluge/zday':
    name = sys.argv[2]
    path = os.path.join(dir, name)
    handleZDay('volume1/video/zday', path)
