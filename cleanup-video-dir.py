#!/usr/bin/python3

import os
import shutil
import tempfile
import re
from sys import argv

MIN_FILE_SIZE = 120 * 1024 * 1024

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


if __name__ == '__main__':
  recycleBin = argv[-1]
  if os.path.exists(recycleBin):
    shutil.rmtree(recycleBin)
  os.makedirs(recycleBin)

  for root in argv[1:-1]:
    files1 = os.listdir(root)
    for file1 in files1:
      path1 = os.path.join(root, file1)
      if os.path.isdir(path1):
        files2 = os.listdir(path1)
        for file2 in files2:
          if re.match("S\\d+", file2):
            path2 = os.path.join(path1, file2)
            cleanup(path2, recycleBin)

  for root in argv[1:-1]:
    cleanup(root, recycleBin)



