#!/usr/bin/python3

import datetime
import duolingo_client
import sys


def is_skill_finished(skill):
  levels = skill['levels']
  finished_levels = skill['finishedLevels']
  return finished_levels == levels


if __name__ == '__main__':
  username = sys.argv[1]
  duo = duolingo_client.Duo(username)
  now = datetime.datetime.now()
  print(now.strftime("%Y-%m-%d (%a)"))

  for i, skill in enumerate(duo.get_skills()):
    levels = skill['levels']
    finished_levels = skill['finishedLevels']
    finished_lessons = skill['finishedLessons']
    if is_skill_finished(skill):
      continue
    if finished_levels < 4 and finished_lessons == 0:
      break

    name = skill['name']
    lessons = skill['lessons']
    strength = int(skill['strength'] * 100)
    print('  %-3d: %-40s Level %d Lesson %2d/%02d %3d%%' % (i, name, finished_levels, finished_lessons, lessons, strength))

  print()

  xp_gains = duo.get_xp_gains()
  lessons_xp = 0
  stories_xp = 0
  for xp_gain in reversed(xp_gains):
    time = datetime.datetime.fromtimestamp(xp_gain['time'])
    if (now - time).days > 0:
      break
    xp = xp_gain['xp']
    if xp % 10 != 0:
      stories_xp += xp
    else:
      lessons_xp += xp

  print('XP Gained in Last 24 Hours:')
  print('  Lessons %d:' % lessons_xp)
  print('  Stories %d:' % stories_xp)
