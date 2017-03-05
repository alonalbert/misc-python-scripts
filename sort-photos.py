#!/usr/bin/python3

import datetime
import os
import shutil
import filecmp
import re
from sys import argv
import tempfile


def isVideo(f):
  m = re.match(".*\.(mp4|avi|mkv)$", f.lower())
  return m is not None


for root in argv[1:]:
  files = os.listdir(root)
  count = 0
  for f in files:
    if f == "Thumbs.db" or f == "breezebrowser.dat":
      continue
    src = os.path.join(root, f)
    if os.path.isdir(src):
      continue

    m = re.match("^(IMG_|VID_|PANO_)?(?P<year>\d\d\d\d)[-]?(?P<month>\d\d)[-]?(?P<day>\d\d).*", f)
    year = None
    if m:
      year = m.group("year")
      month = m.group("month")
      day = m.group("day")
    if year is None or int(year) < 2000 or int(year) > 2050:
      created = int(os.stat(src).st_ctime)
      year = datetime.datetime.fromtimestamp(created).strftime("%Y")
      month = datetime.datetime.fromtimestamp(created).strftime("%m")
      day = datetime.datetime.fromtimestamp(created).strftime("%d")

    if isVideo(f):
      dst = os.path.join(root, "video", year, month)
    else:
      dst = os.path.join(root, year, month, day)

    dstFile = os.path.join(dst, f)
    if os.path.exists(dstFile):
      if filecmp.cmp(src, dstFile, shallow=0):
        # Same file, delete file
        os.remove(src)
        continue
      else:
        # Different file with same name, copy under a new name
        name, ext = os.path.splitext(f)
        dstFile = tempfile.mktemp(ext, name, dst)
    if not os.path.exists(dst):
      os.makedirs(dst)
    shutil.move(src, dstFile)
    count = count + 1
  print("Sorted %d files in %s" % (count, root))
