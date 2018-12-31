#!/usr/bin/python
#

import csv

with open('run/google-ascii.csv', 'rb') as csvfile:
  reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
  for row in reader:
    name = row['Name'].strip()
    if name == '' or not name[0].isalpha():
      continue
    phones = []
    for i in range(5):
      phone = row['Phone %d - Value' % (i + 1)]
      if phone != '':
        phones.append(phone)

    for phone in phones:
      print('%s|%s' % (name, phone))

