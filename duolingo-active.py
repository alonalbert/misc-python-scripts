#!/usr/bin/python3

import argparse
import datetime
import gzip
import json
import os
import pprint
import re
import sys
import requests

from apiclient import discovery
from google.oauth2 import service_account

LOG_FORMAT = '%-20s %-15s %-15s %-10s\n'
LOG_HEADER = LOG_FORMAT % ('Date', 'Lessons XP', 'Stories XP', 'To go')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CONFIG_FILE = os.path.expanduser('~/.duolingo')
SECRET_FILE = os.path.expanduser('~/.duolingo-tracker-client.json')
DAY_ZERO = datetime.datetime(1899, 12, 30)
RANGE = 'Log'
LEVEL_COLOR = [
  '#ce82ff',
  '#1cb0f6',
  '#78c800',
  '#ff4b4b',
  '#ff9600',
]

PP = pprint.PrettyPrinter(indent=2)

CELL_REGEX_FOR_NEW_ROW = re.compile(r'([A-Z]\$)(\d+)')
CELL_REGEX_FOR_OLD_ROWS = re.compile(r'([A-Z]\$?)(\d+)')


class Duo():
  LESSONS = [1, 1, 2, 3, 5]
  LESSONS_TOTAL = []

  def __init__(self, username, token):
    self.LESSONS_TOTAL.append(0)
    i = 0
    for _ in self.LESSONS:
      self.LESSONS_TOTAL.append(self.LESSONS_TOTAL[i] + self.LESSONS[i])
      i += 1

    url = 'https://www.duolingo.com/users/' + username
    self._data = json.loads(requests.get(url, cookies={'jwt_token': token}).content.decode("utf-8"))

  def get_skills(self):
    language_data = self._data['language_data']['es']
    skills = language_data['skills']
    bonus_skills = language_data['bonus_skills']
    return sorted(skills + bonus_skills, key=lambda skill: skill['coords_y'] * 1000 + skill['coords_x'])

  def get_xp_gains(self):
    return self._data['language_data']['es']['calendar']

  def get_total_lessons_for_skill(self, skill):
    level = skill['levels_finished']
    return int(skill['num_sessions_for_level'] / self.LESSONS[level] * self.LESSONS_TOTAL[len(self.LESSONS_TOTAL) - 1])

  def get_num_finished_lessons(self, skill):
    level = skill['levels_finished']
    return self.LESSONS_TOTAL[level] * skill['num_sessions_for_level'] / self.LESSONS[level] + skill[
      'level_sessions_finished']

  def get_data(self):
    return self._data


def undated_formulas_in_row(row, regex):
  for (j, cell) in enumerate(row):
    if isinstance(cell, str) and cell.startswith('='):
      row[j] = regex.sub(lambda m: m.group(1) + str(int(m.group(2)) + 1), cell)


def update_formulas(values):
  undated_formulas_in_row(values[1], CELL_REGEX_FOR_NEW_ROW)
  for (i, row) in enumerate(values[2:]):
    undated_formulas_in_row(row, CELL_REGEX_FOR_OLD_ROWS)


def update_sheet(spreadsheet_id, date, lessons_xp, bonus_xp, stories_xp, finished, total):
  credentials = service_account.Credentials.from_service_account_file(SECRET_FILE, scopes=SCOPES)
  service = discovery.build('sheets', 'v4', credentials=credentials)
  values_api = service.spreadsheets().values()
  request = values_api.get(spreadsheetId=spreadsheet_id, range=RANGE, valueRenderOption='FORMULA')
  response = request.execute()
  values = response['values']
  span = date - DAY_ZERO
  new_day = int(values[1][0]) != span.days
  if new_day:
    values.insert(1, values[1].copy())
    update_formulas(values)

  if new_day \
      or values[1][1] != lessons_xp \
      or values[1][2] != bonus_xp \
      or values[1][3] != stories_xp \
      or values[1][4] != finished \
      or values[1][5] != total:
    values[1][0] = span.days + (span.seconds / (24 * 60 * 60))
    values[1][1] = lessons_xp
    values[1][2] = bonus_xp
    values[1][3] = stories_xp
    values[1][4] = finished
    values[1][5] = total

    body = {
      'values': values
    }
    request = values_api.update(spreadsheetId=spreadsheet_id, range=RANGE, valueInputOption='USER_ENTERED',
                                body=body)
    request.execute()


def _almost_finished(skill):
  lessons = skill['num_sessions_for_level']
  return lessons / 5 * 3


def is_skill_finished(skill):
  levels = skill['num_levels']
  finished_levels = skill['levels_finished']
  finished_lessons = skill['level_sessions_finished']
  return finished_levels == levels or finished_levels == 4 and finished_lessons >= _almost_finished(skill)


def is_skill_almost_finished(skill):
  finished_levels = skill['levels_finished']
  finished_lessons = skill['level_sessions_finished']
  return finished_levels == 4 and 20 > finished_lessons >= _almost_finished(skill)


def get_lessons_counts(skills):
  total = 0
  finished = 0
  for skill in skills:
    levels = skill['num_levels']
    lessons = skill['num_sessions_for_level']
    finished_levels = skill['levels_finished']
    finished_lessons = skill['level_sessions_finished']
    if finished_levels == levels:
      skill_total = finished_lessons
      skill_finished = finished_lessons
    else:
      base_lessons = lessons / Duo.LESSONS[finished_levels]
      skill_total = base_lessons * Duo.LESSONS_TOTAL[levels]
      skill_finished = Duo.LESSONS_TOTAL[finished_levels] * base_lessons + finished_lessons

    total += skill_total
    finished += skill_finished

  return finished, total


def print_line(is_html, line):
  if is_html:
    print('%s<br/>' % line)
  else:
    print(line)


class Row:
  def __init__(self, skill, index, name, finished_levels, finished_lessons, lessons, total_finished_levels,
               total_lessons_for_skill, strength, is_html,
               is_next):
    self.skill = skill
    self.index = index
    self.name = name
    self.finished_levels = finished_levels
    self.finished_lessons = finished_lessons
    self.lessons = lessons
    self.total_finished_levels = total_finished_levels
    self.total_lessons_for_skill = total_lessons_for_skill
    self.strength = strength
    self._is_html = is_html
    self.is_next = is_next

  def print(self):
    lessons = int(self.lessons if self.finished_levels < 4 else _almost_finished(self.skill))
    if is_html:
      print('<tr style="background: %s; font-weight: %s">' % (
        LEVEL_COLOR[self.finished_levels], 'bold' if self.is_next else 'normal'))
      print('  <td style="padding:0 10px">%s</td>' % self.index)
      print('  <td style="padding"0 10px">%s</td>' % self.name)
      # print('  <td style="padding"0 10px">Level %s</td>' % self.finished_levels)
      print('  <td style="padding:0 10px">%s/%s</td>' % (self.finished_lessons, lessons))
      print('  <td style="padding:0 10px">%s%%</td>' % self.strength)
      print('  <td style="padding:0 0px, 0, 10px; text-align: right">%d</td>' % (self.total_finished_levels))
      print('  <td style="padding:0 3px">/</td>')
      print('  <td style="padding:0 10px 0 0px">%d</td>' % (self.total_lessons_for_skill))
      if self.is_next:
        text = '<====='
        href = 'https://www.duolingo.com/skill/%s/%s/%d' % (
        self.skill['language'], self.skill['url_title'], self.finished_lessons + 1)

        print(
          '  <td style="background: #ffffff; padding:0 10px;"><a href="%s" style="text-decoration: none;">%s</a></td>' % (
            href, text))
      print('</tr>')
    else:
      print('  %-3d: %-40s Level %d Lesson %2d/%02d  %-8s %3d%% %s' % (
        self.index,
        self.name,
        self.finished_levels,
        self.finished_lessons,
        lessons,
        '%4d/%d' % (self.total_finished_levels, self.total_lessons_for_skill),
        self.strength,
        '  <====' if self.is_next else ''))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Daily Duolingo Activity.')

  parser.add_argument('--sheet', help='Google sheet for daily log')
  parser.add_argument('--status_file', help='Status file name', default=None)

  parser.add_argument('--html', dest='html', help='Print status in HTML', action='store_true')
  parser.add_argument('--no-html', dest='html', help='Print status in text', action='store_false')
  parser.set_defaults(html=False)

  parser.add_argument('--out', help='Output dir', default=None)
  parser.add_argument('--zip', dest='zip', help='Zip data', action='store_true')
  parser.add_argument('--no-zip', dest='zip', help="Don't zip data", action='store_false')
  parser.set_defaults(zip=False)

  args = parser.parse_args()

  with open(CONFIG_FILE) as f:
    config = json.load(f)

  duo = Duo(config['user'], config['token'])

  if args.status_file:
    status_file = open(args.status_file, 'w')
    sys.stdout = status_file
  else:
    status_file = None

  now = datetime.datetime.now()

  date = now.strftime("%Y-%m-%d (%a)")
  is_html = args.html
  if is_html:
    print('<html>\n<header>\n</header>\n<body>')
    print('<h2>%s</h2>' % date)
    print('<table style="border-collapse: collapse"><tbody>')
  else:
    print(date)

  almost_finished = 0
  active = 0
  skills = duo.get_skills()
  total_finished_levels = 0
  rows = []
  for index, skill in enumerate(skills):
    n = len(rows)
    levels = skill['num_levels']
    finished_levels = skill['levels_finished']
    finished_lessons = skill['level_sessions_finished']
    if is_skill_finished(skill):
      if is_skill_almost_finished(skill):
        almost_finished += 1
      continue

    active += 1
    name = skill['title']
    lessons = skill['num_sessions_for_level']
    strength = int(skill['strength'] * 100)
    total_finished_levels = duo.get_num_finished_lessons(skill)
    total_lessons_for_skill = duo.get_total_lessons_for_skill(skill)
    if n == 0:
      is_next = True
    else:
      is_next = False
      first_row = rows[0]
      for i in range(1, n + 1, 1):
        if first_row.is_next and rows[n - i].total_finished_levels == total_finished_levels + 4 * i + 1:
          is_next = True
          first_row.is_next = False
          break

    rows.append(
      Row(skill, index, name, finished_levels, finished_lessons, lessons, total_finished_levels,
          total_lessons_for_skill,
          strength, is_html, is_next))

  for row in rows:
    row.print()

  if is_html:
    print('</tbody></table>')

  xp_gains = duo.get_xp_gains()
  lessons_xp = 0
  bonus_xp = 0
  stories_xp = 0

  from_date = datetime.datetime(now.year, now.month, now.day)
  to_date = from_date + datetime.timedelta(days=1)

  xp_total = 0
  for xp_gain in reversed(xp_gains):
    time = datetime.datetime.fromtimestamp(xp_gain['datetime'] / 1000)
    if (now - time).days > 0:
      break
    if from_date <= time < to_date:
      xp = xp_gain['improvement']
      xp_total += xp
      is_story = 20 < xp < 50

      if is_story:
        stories_xp += xp
      else:
        if xp == 20:
          lessons_xp += 20
        else:
          lessons_xp += 10
          bonus_xp += xp - 10

  print_line(is_html, 'Almost finished: %d Active: %s' % (almost_finished, active))
  print_line(is_html, 'XP Gained today: %d' % xp_total)
  print_line(is_html, '  Lessons %d:' % lessons_xp)
  print_line(is_html, '  Bonus %d:' % bonus_xp)
  print_line(is_html, '  Stories %d:' % stories_xp)
  finished, total = get_lessons_counts(skills)
  print_line(is_html, 'Skills: %d' % len(skills))
  print_line(is_html, 'Lessons: %d/%d' % (finished, total))

  if is_html:
    print('</body></html>')

  if status_file:
    status_file.close()

  if args.sheet:
    update_sheet(args.sheet, now, lessons_xp, bonus_xp, stories_xp, finished, total)

  if args.out is not None:
    dataJson = json.dumps(duo.get_data(), indent=2)
    os.makedirs(args.out, exist_ok=True)
    ext = 'gz' if args.zip else 'json'
    adjustedNow = now - datetime.timedelta(minutes=1)
    filename = adjustedNow.strftime('%Y-%m-%d-duolingo-data.') + ext
    if args.zip:
      writer = gzip.open
      data = dataJson.encode()
    else:
      writer = open
      data = dataJson
    with writer(os.path.join(args.out, filename), 'w') as f:
      f.write(data)
