#!/usr/bin/python3

from sys import argv

name = ''
size = 0
with open(argv[1]) as f:
  for line in f:
    if line.startswith('  name: "'):
      name = line[9:-2]

    if line.startswith('  total_size: '):
      size = line[14:-1]
      print("%s: %s" % (name, size))

