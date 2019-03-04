#!/usr/bin/python

import datetime
import duolingo_client
import sys

if __name__ == '__main__':
  username = sys.argv[1]
  duo = duolingo_client.Duo(username)
  now = datetime.datetime.now()
  print(now.strftime("%Y-%m-%d (%a)"))

  for i, skill in enumerate(duo.get_skills()):
    levels = skill['levels']
    finished_levels = skill['finishedLevels']
    finished_lessons = skill['finishedLessons']
    if finished_levels != levels and finished_lessons != 0:
      name = skill['name']
      lessons = skill['lessons']
      strength = int(skill['strength'] * 100)
      print('  %-3d: %-40s Level %d Lesson %2d/%02d %3d%%' % (i, name, finished_levels, finished_lessons, lessons, strength))

  print
