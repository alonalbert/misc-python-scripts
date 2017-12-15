#!/usr/bin/python3
#
import os
import shutil
import re

from sys import argv
from subprocess import call

RAR_EXT = ".rar"
CAT_PREFIX = "unrar-"

outDir = argv[1]
cat = argv[2]
path = argv[3]
name = argv[4]


def getRarFile(path: str):
  if os.path.isfile(path) and path.endswith(".rar"):
    return path

  files = os.listdir(path)
  for file in files:
    if file.endswith(".rar"):
      return os.path.join(path, file)

def handleZDay(outDir: str, rarFile: str, name: str):
  macth = re.search(r"^([^.]*).(\d\d.\d\d.\d\d).(.*).XXX.*", name, re.IGNORECASE)

  if not macth:
    print("ZDAY: Can't match %s" % name)
    return

  series =  re.sub(r"(([0-9]+)|([A-Z][a-z]*))", r"\1 ", macth.group(1)).strip()
  date = macth.group(2).replace(".", "-")
  episode = macth.group(3).replace(".", " ")

  dir = "%s/video/zday/%s" % (outDir, series)
  tmpDir = "%s/tmp" % (dir)
  os.makedirs(tmpDir, exist_ok=True)

  print("Extracting %s" % rarFile)
  call(["unrar", "-o-", "-inul", "x", rarFile], cwd=tmpDir)
  videoFile = os.listdir(tmpDir)[0]

  src = "%s/%s" % (tmpDir, videoFile)
  dest = "%s/%s %s%s" % (dir, date, episode, os.path.splitext(videoFile)[1])

  shutil.move(src, dest)
  shutil.rmtree(tmpDir)

def extractArchive(rarFile: str, dest: str):
  print("Extracting %s to %s" % (rarFile, dest))
  os.makedirs(dest, exist_ok=True)
  call(["unrar", "-o-", "-inul", "x", rarFile], cwd=dest)

def process(outDir: str, cat: str, path: str, name: str):
  if not cat.startswith(CAT_PREFIX):
    return
  rarFile = getRarFile(path)
  if rarFile == None:
    return

  if cat == "unrar-zday":
    handleZDay(outDir, rarFile, name)
  else:
    extractArchive(rarFile, outDir + "/" + cat[len(CAT_PREFIX):].replace("-", "/"))

process(outDir, cat, path, name)
