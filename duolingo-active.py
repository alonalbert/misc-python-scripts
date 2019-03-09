#!/usr/bin/python3

import argparse
import datetime
import os
import sys

from duolingo_client import Duo
from apiclient import discovery
from google.oauth2 import service_account

LOG_FORMAT = '%-20s %-15s %-15s %-10s\n'
LOG_HEADER = LOG_FORMAT % ('Date', 'Lessons XP', 'Stories XP', 'To go')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SECRET_FILE = os.path.expanduser('~/.duolingo-tracker-client.json')
DAY_ZERO = datetime.datetime(1899, 12, 30)
RANGE = 'Log'


def update_sheet(spreadsheet_id, date, lessons_xp, stories_xp, to_go):
    credentials = service_account.Credentials.from_service_account_file(SECRET_FILE, scopes=SCOPES)
    service = discovery.build('sheets', 'v4', credentials=credentials)
    values_api = service.spreadsheets().values()
    request = values_api.get(spreadsheetId=spreadsheet_id, range=RANGE, valueRenderOption='FORMULA')
    response = request.execute()
    values = response['values']
    span = date - DAY_ZERO
    values.insert(1, [span.days, lessons_xp, stories_xp, to_go])
    body = {
        'values': values
    }
    request = values_api.update(spreadsheetId=spreadsheet_id, range=RANGE, valueInputOption='USER_ENTERED', body=body)
    request.execute()


def is_skill_finished(skill):
    levels = skill['levels']
    finished_levels = skill['finishedLevels']
    finished_lessons = skill['finishedLessons']
    return finished_levels == levels or finished_levels == 4 and finished_lessons >= 10

def is_skill_almost_finished(skill):
    finished_levels = skill['finishedLevels']
    finished_lessons = skill['finishedLessons']
    return finished_levels == 4 and 20 > finished_lessons >= 10


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

    return int(course_total - course_finished)


def print_line(is_html, line):
    if is_html:
        print('%s<br/>' % line)
    else:
        print(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Daily Duolingo Activity.')

    parser.add_argument('user', help='Duolingo user name')
    parser.add_argument('--sheet', help='Google sheet for daily log')
    parser.add_argument('--status_file', help='Status file name', default=None)

    parser.add_argument('--html', dest='html', help='Print status in HTML', action='store_true')
    parser.add_argument('--no-html', dest='html', help='Print status in text', action='store_false')
    parser.set_defaults(html=False)

    args = parser.parse_args()

    duo = Duo(args.user)

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
        print('<table><tbody>')
    else:
        print(date)

    almost_finished = 0
    active = 0
    for i, skill in enumerate(duo.get_skills()):
        levels = skill['levels']
        finished_levels = skill['finishedLevels']
        finished_lessons = skill['finishedLessons']
        if is_skill_finished(skill):
            if is_skill_almost_finished(skill):
                almost_finished += 1
            continue
        if finished_levels < 4 and finished_lessons == 0:
            break
        active += 1
        name = skill['name']
        lessons = skill['lessons']
        strength = int(skill['strength'] * 100)
        if is_html:
            print('<tr>')
            print('  <td>%s</td>' % i)
            print('  <td>%s</td>' % name)
            print('  <td>Level %s</td>' % finished_levels)
            print('  <td>Lesson %s/%s</td>' % (finished_lessons, lessons))
            print('  <td>%s%%</td>' % strength)
            print('</tr>')
        else:
            print('  %-3d: %-40s Level %d Lesson %2d/%02d %3d%%' % (
                i, name, finished_levels, finished_lessons, lessons, strength))
    if is_html:
        print('</tbody></table>')

    xp_gains = duo.get_xp_gains()
    lessons_xp_24h = 0
    stories_xp_24h = 0

    lessons_xp_today = 0
    stories_xp_today = 0

    from_date = datetime.datetime(now.year, now.month, now.day)
    if now.hour < 1:
        from_date -= datetime.timedelta(days=1)
    to_date = from_date + datetime.timedelta(days=1)

    for xp_gain in reversed(xp_gains):
        time = datetime.datetime.fromtimestamp(xp_gain['time'])
        if (now - time).days > 0:
            break
        xp = xp_gain['xp']
        is_story = 10 < xp < 50
        if is_story:
            stories_xp_24h += xp
        else:
            lessons_xp_24h += xp

        if from_date <= time < to_date:
            if is_story:
                stories_xp_today += xp
            else:
                lessons_xp_today += xp

    print_line(is_html, 'Almost finished: %d Active: %s' % (almost_finished, active))
    print_line(is_html, 'XP Gained in Last 24 Hours:')
    print_line(is_html, '  Lessons %d:' % lessons_xp_24h)
    print_line(is_html, '  Stories %d:' % stories_xp_24h)
    print_line(is_html, 'XP Gained today:')
    print_line(is_html, '  Lessons %d:' % lessons_xp_today)
    print_line(is_html, '  Stories %d:' % stories_xp_today)
    lessons_to_go = get_uncompleted_lessons_count(duo.skills)
    print_line(is_html, 'Lessons to go: %d' % lessons_to_go)

    if is_html:
        print('</body></html>')

    if status_file:
        status_file.close()

    if args.sheet:
        update_sheet(args.sheet, from_date, lessons_xp_today, stories_xp_today, lessons_to_go)
