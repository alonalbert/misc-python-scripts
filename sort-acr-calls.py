import os
from datetime import datetime


files = os.listdir(os.path.expanduser('~/tmp/ACRCalls/'))

numbers = set([])

for file in files:
    direction = file[0:1]
    timestamp = datetime.strftime(datetime.strptime(file[2:16], '%Y%m%d%H%M%S'), '%Y.%m.%d.%H.%M.%S')
    phone_number = file[17:-4]
    numbers.add(phone_number)
    # print('%s:   %s.%s.[%s].m4a' % (file, phone_number, timestamp, direction))

for number in numbers:
    print number