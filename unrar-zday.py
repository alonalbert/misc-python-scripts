#!/usr/bin/python
#

import os
import re
import shutil
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
  macth = re.search(r"^(?P<series>[^.]*).(?P<episode>(\d\d.\d\d.\d\d)|(E\d+)).(?P<title>.*).XXX.*", name, re.IGNORECASE)

  if not macth:
    print("ZDAY: Can't match %s" % name)
    return

  series =  re.sub(r"(([0-9]+)|([A-Z][a-z]*))", r"\1 ", macth.group('series')).strip()
  episode = macth.group('episode').replace(".", "-")
  title = macth.group('title').replace(".", " ")

  dir = "%s/%s" % (outDir, series)
  tmpDir = "%s/tmp" % (dir)
  Path(tmpDir).mkdir(parents=True)

  print("Extracting %s" % rarFile)
  call(["unrar", "-o-", "-inul", "x", rarFile], cwd=tmpDir)
  videoFile = os.listdir(tmpDir)[0]

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
