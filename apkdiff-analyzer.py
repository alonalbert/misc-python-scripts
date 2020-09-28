#!/usr/bin/python3

from sys import argv

def get_new_types(app):
  types = []
  with open(app + '-apkdiff.txt') as f:
    in_types_section = False
    for line in f:
      line = line.strip()
      if not in_types_section:
        if line == '∆|value':
          in_types_section = True
        continue
      if line == '':
        break
      if line.startswith('+') or '[]' in line:
        continue
      types.append(line[2:])
  return types

def get_real_names(app):
  names = {}
  with open(app + '-proguard.map') as f:
    for line in f:
      if line[0] == ' ':
        continue
      line = line.strip()
      split = line.split(' -> ')
      names[split[0]] = split[1][0:-1]
  return names

def get_sizes(app):
  sizes = {}
  with open(app + '-dex2jar.txt') as f:
    for line in f:
      split = line.strip().split(' ')
      # print('%s:%d' % (split[7].split('.')[0], int(split[0].strip())))
      sizes[split[7].split('.')[0].replace('/', '.')] = int(split[0].strip())
  return sizes

class Type():
  def __init__(self, name, size):
    self._name = name
    self._size = size

  def __lt__(self, other):
    return self._size < other._size

  def __str__(self):
    return '%-10d: %s' % (self._size, self._name)

if __name__ == '__main__':
  app = argv[1]
  sizes = get_sizes(app)
  type_names = get_new_types(app)
  names = get_real_names(app)

  types = []
  for type in type_names:
    if type in names:
      name = names[type]
    else:
      name = type
    if name in sizes:
      types.append(Type(type, sizes[name]))
    elif not (name.startswith('java') or name.startswith('android') or name.endswith('package-info')):
      print('%s not found' % name)

  types.sort()
  total = 0
  package_map = {}

  print("Classes:")
  for type in reversed(types):
    total += type._size
    package = type._name[0:type._name.rfind('.')]
    if package in package_map:
       size = package_map[package]
    else:
      size = 0
    package_map[package] = size + type._size

    print(type)

  packages = []
  for package, size in package_map.items():
      packages.append(Type(package, size))
  packages.sort()


  print("\nPackages:")
  for package in reversed(packages):
    print(package)

  print("\nTotal: %d" % total)
