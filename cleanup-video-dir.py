#!/usr/bin/python3

import os
import shutil
import tempfile
from sys import argv

MIN_FILE_SIZE = 50 * 1024 * 1024

def countLargeFiles(dir):
  files = os.listdir(dir)
  count = 0
  for file in files:
    path = os.path.join(dir, file)
    if os.path.isfile(path):
      fileSize = os.path.getsize(path)
      if fileSize > MIN_FILE_SIZE:
        count += 1
    else:
      count += countLargeFiles(path)
  return count

def cleanup(root, recycleBin):
  files = os.listdir(root)
  for file in files:
    path = os.path.join(root, file)
    if os.path.isdir(path):
      count = countLargeFiles(path)
      if count == 0:
        print("Removing %s" % path)
        dest = tempfile.mkdtemp("", file, recycleBin)
        shutil.move(path, dest)

recycleBin = argv[-1]
if os.path.exists(recycleBin):
  shutil.rmtree(recycleBin)
os.makedirs(recycleBin)
for root in argv[1:-1]:
  print("Cleaning up %s" % root)
  cleanup(root, recycleBin)
