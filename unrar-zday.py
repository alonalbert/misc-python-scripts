#!/usr/bin/python
#

import os
import re
import shutil
import datetime
import sys
from pathlib import Path

from subprocess import call

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

if __name__ == '__main__':
  dir = sys.argv[3]
  if dir == '/nas/video/deluge/zday':
    name = sys.argv[2]
    path = os.path.join(dir, name)
    handleZDay('/nas/video/zday', path)
