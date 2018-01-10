#!/usr/bin/python
#

import requests
import configparser
import sys
import os

if __name__ == '__main__':
  dir = sys.argv[3]
  name = sys.argv[2]
  config = configparser.ConfigParser()
  config.read(os.path.expanduser('~/.pushover'))
  setup = config["setup"]
  if dir != '/nas/video/deluge/tv':
    requests.post('https://api.pushover.net/1/messages.json',
                  data={
                    'user': setup['user'],
                    'token': setup['deluge-token'],
                    'sound': 'magic',
                    'message': name
                  })
