#!/usr/bin/python3

import datetime
from duolingo_client import Duo
import sys


def is_skill_finished(skill):
    levels = skill['levels']
    finished_levels = skill['finishedLevels']
    return finished_levels == levels


def get_uncompleted_lessons_count(skills):
    course_total = 0
    course_finished = 0
    for skill in skills:
        levels = skill['levels']
        lessons = skill['lessons']
        finished_levels = skill['finishedLevels']
        finished_lessons = skill['finishedLessons']
        if finished_levels == levels:
            skill_total = finished_lessons
            skill_finished = finished_lessons
        else:
            base_lessons = lessons / Duo.LESSONS[finished_levels]
            skill_total = base_lessons * Duo.LESSONS_TOTAL[levels]
            skill_finished = Duo.LESSONS_TOTAL[finished_levels] * base_lessons + finished_lessons

        course_total += skill_total
        course_finished += skill_finished

    return course_total - course_finished


if __name__ == '__main__':
    username = sys.argv[1]
    duo = Duo(username)
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
        print('  %-3d: %-40s Level %d Lesson %2d/%02d %3d%%' % (
        i, name, finished_levels, finished_lessons, lessons, strength))

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

    print('Lessons to go %d:' % get_uncompleted_lessons_count(duo.skills))

    print()
