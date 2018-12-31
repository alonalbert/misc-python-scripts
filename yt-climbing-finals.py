#!/usr/bin/python
from datetime import datetime

from youtube import YouTube
import re

UIAA = 'UIAA - International Climbing and Mountaineering'
USC = 'USA Climbing'
IFSC = 'International Federation of Sport Climbing'

CHANNELS = {
  IFSC,
  USC,
  UIAA
}

IFSE_EXCLUDE = re.compile('Semi|Youth|Speed|Paraclimbing|Highlights')
USC_EXCLUDE = re.compile('Youth|Collegiate|Speed|Qualification|Semi|(On the Road)|(Road to)|Junior')
UIAA_EXCLUDE = re.compile('Semi|Youth|Speed|Paraclimbing|Highlights')

youtube = YouTube()


def channelFilter(channel):
  title = channel.title
  return title in CHANNELS


def videoFilter(channel, video):
  videoTitle = video.title
  channelTitle = channel.title
  if channelTitle == IFSC:
    return 'Finals' in videoTitle and not IFSE_EXCLUDE.search(videoTitle)
  elif channelTitle == USC:
    return USC_EXCLUDE.search(videoTitle)
  elif channelTitle == UIAA:
    return 'Finals' in videoTitle and not UIAA_EXCLUDE.search(videoTitle)
  else:
    return True

youtube.addVideosToPlaylist(
  'Climbing Finals',
  'Final round of climbing competitions',
  datetime(2018, 8, 20),
  '~/.youtube-climbing-finals-history',
  lambda channel: channelFilter(channel),
  lambda channel, video: videoFilter(channel, video))
