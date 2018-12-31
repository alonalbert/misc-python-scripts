#!/usr/bin/python2.7
#
import requests
import configparser
import datetime
import logging
import os
import sys
import traceback
import glob

from deluge.ui.client import client
from twisted.internet import reactor, defer

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

class Main:
  # If this is true, will only print stuff. Won't actually delete anything
  fakeDelete = True
  plexFiles = set([])
  watchedFiles = {}

  config = None

  def __init__(self, fakeDelete):
    self.config = configparser.ConfigParser()
    self.config.read(os.path.expanduser('~/.plex-delete-watched'))
    pass

  def run(self):
    self.processTorrents()

    reactor.run()





  @defer.inlineCallbacks
  def processTorrents(self):
    delugeConfig = self.config['Deluge']

    try:
      yield client.connect(host=delugeConfig['host'], username=delugeConfig['username'],
                           password=delugeConfig['password'])
      torrents = yield client.core.get_torrents_status({}, [])

      for torrentId, torrent in torrents.iteritems():
        if torrent["state"] == 'Error':
          name = torrent['name']
          path = find(name, '/volume1/video/tv')
          if path is not None:
            print('Linking %s' % (name))
            try:
              os.link(path, os.path.join('/volume1/video/deluge/tv', name))
            except:
              continue

    except Exception as e:
      traceback.print_exc()

    finally:
      client.disconnect()
      reactor.stop()

def find(name, path):
  for root, dirs, files in os.walk(path):
    if name in files:
      return os.path.join(root, name)
  return None


if __name__ == '__main__':
  fake = False
  if len(sys.argv) > 1 and sys.argv[1] == '--fake':
    fake = True
  Main(fake).run()
