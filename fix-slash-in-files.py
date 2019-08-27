#!/usr/bin/python3
import os

import sys

if __name__ == '__main__':
  dir = sys.argv[1]

  for filename in os.listdir(dir):
    print(filename)
    fixed = filename.replace('\\', '/')
    dirname = os.path.dirname(fixed)
    basename = os.path.basename(fixed)

    os.makedirs(os.path.join(dir, dirname), exist_ok=True)
    os.rename(os.path.join(dir, filename), os.path.join(dir, dirname, basename))
