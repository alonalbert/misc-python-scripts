#!/usr/bin/python
#

import requests
import configparser
import sys
import os


def get_config_filename():
  home_dir = os.path.expanduser('~/.pushover')
  return home_dir if os.path.exists(home_dir) else os.path.dirname(os.path.realpath(__file__)) + '/.pushover'

if __name__ == '__main__':
  dir = sys.argv[3]
  name = sys.argv[2]
  config = configparser.ConfigParser()
  config.read(get_config_filename())
  setup = config["setup"]
  if not (dir.endswith('/tv') or dir.endswith('/zday')):
    requests.post('https://api.pushover.net/1/messages.json',
                  data={
                    'user': setup['user'],
                    'token': setup['deluge-token'],
                    'sound': 'magic',
                    'message': name
                  })
