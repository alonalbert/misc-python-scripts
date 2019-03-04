#!/usr/bin/python

import json
import os.path
import requests
import textwrap

BASE_URL = 'https://www.duolingo.com'
LOGIN_URL = BASE_URL + '/login'
URL = BASE_URL + '/2017-06-30/users/%s?fields=currentCourse'
LESSONS = [1, 1, 2, 3, 5]
LESSONS_TOTAL = []


def get_password():
  with open(os.path.expanduser('~/.duolingo-password')) as f:
    return f.read().strip()


class Duo:
  def __init__(self, username, password=get_password()):
    LESSONS_TOTAL.append(0)
    i = 0
    for _ in LESSONS:
      LESSONS_TOTAL.append(LESSONS_TOTAL[i] + LESSONS[i])
      i += 1

    login_response = requests.post(LOGIN_URL, data={'login': username, 'password': password})
    token = login_response.headers['jwt']
    user_id = json.loads(login_response.content)['user_id']

    url = URL % user_id
    self._data = json.loads(requests.get(url, headers={'authorization': 'Bearer %s' % token}).content)
    self.skills = []
    for row in self._data['currentCourse']['skills']:
      for skill in row:
        if skill.get('accessible', False):
          self.skills.append(skill)

  def get_skills(self):
    return self.skills

  def print_topics(self):
    course_total = 0
    course_finished = 0
    for skill in self.skills:
      name = skill['name']
      strength = int(skill['strength'] * 100)
      levels = skill['levels']
      lessons = skill['lessons']
      finished_levels = skill['finishedLevels']
      finished_lessons = skill['finishedLessons']
      if finished_levels == levels:
        skill_total = finished_lessons
        skill_finished = finished_lessons
      else:
        base_lessons = lessons / LESSONS[finished_levels]
        skill_total = base_lessons * LESSONS_TOTAL[levels]
        skill_finished = LESSONS_TOTAL[finished_levels] * base_lessons + finished_lessons

      course_total += skill_total
      course_finished += skill_finished

      print('%-40s %3d/%3d (%d) @ %d' % (name, skill_finished, skill_total, skill_total - skill_finished,
                                         strength))

    print('%-40s %3d/%3d (%d)' % ('Total', course_finished, course_total, course_total - course_finished))

  def get_tips(self):
    i = 0
    for skill in self.skills:
      explanation = skill.get('explanation', None)
      if explanation:
        i += 1
        title = explanation['title']
        print('Fetching %s' % title)
        filename = '%02d-%s.txt' % (i, title.replace(' ', '-'))
        url = explanation['url']
        tips = json.loads(requests.get(url).content)
        elements = tips['elements']
        with open(filename, 'w') as f:
          first = True
          for element in elements:
            if element['type'] == 'text':
              styled_string = element['element']['styledString']
              text = styled_string['text']
              styling = styled_string['styling']
              if not first and styling[0]['to'] == len(text):
                f.write('\n')
              f.write('%s\n' % textwrap.fill(text.encode('utf8')))
              first = False

if __name__ == '__main__':
  duo = Duo('AlonAlbert')
  # duo.get_tips()
  # duo.print_topics()
