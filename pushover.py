#!/usr/bin/python
#

import requests
import configparser
import os
import argparse

if __name__ == '__main__':
  config = configparser.ConfigParser()
  config.read(os.path.expanduser('~/.pushover'))
  setup = config["setup"]
  tokens = {}
  for name, value in setup.iteritems():
    if name.endswith('-token'):
      tokens[name[:-6]] = value

  user = setup['user']
  parser = argparse.ArgumentParser(description='Send a pushover message.')
  parser.add_argument('app', help='App token to use', choices=tokens.keys())
  parser.add_argument('message', help='Message to send')

  parser.add_argument('--title', help='Title of notification')
  parser.add_argument('--url', help='URL to open')
  parser.add_argument('--url_title', help='URL text')
  parser.add_argument('--device', help='Device to send to')
  parser.add_argument('--sound', help='Sound of notification', choices=[
    'pushover',
    'bike',
    'bugle',
    'cashregister',
    'classical',
    'cosmic',
    'falling',
    'gamelan',
    'incoming',
    'intermission',
    'magic',
    'mechanical',
    'pianobar',
    'siren',
    'spacealarm',
    'tugboat',
    'alien',
    'climb',
    'persistent',
    'echo',
    'updown',
    'none',
  ])
  parser.add_argument('--priority', type=int, help='Priority of notification', choices=[
    -2,
    -1,
    1,
    2,
  ])

  parser.add_argument('--retry', type=int, help='Priority of notification', default=60)
  parser.add_argument('--expire', type=int, help='Priority of notification', default=3660)
  parser.add_argument('--attachment', help='Image attachment')

  args = parser.parse_args()

  data = {
    'user': user,
    'token': tokens[args.app],
    'message': args.message,
    'title': args.title,
    'url': args.url,
    'url_title': args.url_title,
    'device': args.device,
    'sound': args.sound,
    'priority': args.priority,
  }

  if args.priority == 2:
    data['retry'] = args.retry
    data['expire'] = args.expire

  files = None
  if args.attachment is not None:
    files = {
      'attachment': open(args.attachment, 'rb')
    }


  try:
    response = requests.post('https://api.pushover.net/1/messages.json', data=data, files=files)
    if response.status_code != 200:
      print(response.content)
      exit(1)
  except requests.exceptions.RequestException as e:
    print(e)

