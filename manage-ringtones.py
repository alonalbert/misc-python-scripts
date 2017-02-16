#!/usr/bin/python3
#

from optparse import OptionParser

import filecmp
import os
import shutil
import subprocess


def backup(directory):
    print('Backing up device ringtones')
    pull('/sdcard/Ringtones', directory)
    pull('/sdcard/Notifications', directory)
    pull('/sdcard/Alarms', directory)
    pass


def restore(directory):
    print('Restoring device ringtones')
    subprocess.call(['adb', 'root'])

    restoreSection('Ringtones', directory)
    restoreSection('Notifications', directory)
    restoreSection('Alarms', directory)
    pass

def restoreSection(section, directory):
    push('%s/%s' % (directory, section), '/sdcard/')
    lines = subprocess.check_output(['adb', 'shell', 'ls', '/system/media/audio/%s/' % section.lower()]).decode("utf-8")
    systemFiles = lines.split()
    for file in systemFiles:
        subprocess.call(['adb', 'shell', 'rm', '-f', '/sdcard/%s/%s' %(section, file)])
    pass


def get(directory):
    print('Copying system ringtones from device')
    subprocess.call(['adb', 'root'])
    getSection('ringtones', directory)
    getSection('notifications', directory)
    getSection('alarms', directory)
    pass


def getSection(section, directory):
    tmpDir = directory + '/tmp'
    localSection = section.capitalize()
    pull('/system/media/audio/' + section, tmpDir)
    files = os.listdir(tmpDir)
    dstDir = '%s/%s' % (directory, localSection)
    for file in files:
        src = tmpDir + '/' + file
        dst = '%s/%s' % (dstDir, file)
        if os.path.exists(dst):
            if filecmp.cmp(src, dst, shallow=False):
                os.remove(dst)
            else:
                os.remove(src)
                continue
        shutil.move(src, dst)
    os.removedirs(tmpDir)
    pass


def pull(fromDir, toDir):
    subprocess.call(['adb', 'pull', fromDir, toDir])
    pass


def push(fromDir, toDir):
    subprocess.call(['adb', 'push', fromDir, toDir])
    pass


usage = "usage: %prog [options] backup|restore|get"
parser = OptionParser(usage=usage)
parser.add_option("-d", "--dir", dest="dir", default='.', help="Backup/Restore directory", metavar="DIR")

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.print_usage()
    exit(1)

command = args[0]

directory = options.dir

if os.path.exists(directory):
    if not os.path.isdir:
        print('Path is not a directory: %s' % (directory))

os.makedirs(directory + "/Ringtones", exist_ok=True)
os.makedirs(directory + "/Alarms", exist_ok=True)
os.makedirs(directory + "/Notifications", exist_ok=True)

if 'backup'.startswith(command):
    backup(directory)
elif 'restore'.startswith(command):
    restore(directory)
elif 'get'.startswith(command):
    get(directory)
else:
    print('Invalid command: %s' % (command))
    parser.print_usage()
    exit(1)
