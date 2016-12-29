import os
import shutil
from sys import argv

MIN_FILE_SIZE = 50 * 1024 * 1024

def cleanup(dir, dest):
    files = os.listdir(dir)
    count = 0
    for file in files:
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            fileSize = os.path.getsize(path)
            if fileSize > MIN_FILE_SIZE:
                count += 1
        else:
            count += cleanup(path, dest)
    basedir = os.path.basename(dir)
    if basedir.lower() != "sample" and count == 0:
        target = dest + "/" + basedir
        if os.path.exists(target):
          i = 1
          target = dest + "/" + basedir + "-" + str(i)
          while os.path.exists(target):
            i += 1
            target = dest + "/" + basedir + "-" + str(i)
        print "%s -> %s" % (dir, target)
        shutil.move(dir, target)

    return count


cleanup(argv[1], argv[2])
