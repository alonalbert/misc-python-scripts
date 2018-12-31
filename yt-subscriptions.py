#!/usr/bin/python
from datetime import datetime

from youtube import YouTube

UIAA = 'UIAA - International Climbing and Mountaineering'
USC = 'USA Climbing'
IFSC = 'International Federation of Sport Climbing'

EXCLUDE_CHANNELS = {
  IFSC,
  USC,
  UIAA
}

youtube = YouTube()

def channelFilter(channel):
  return channel.title not in EXCLUDE_CHANNELS


def videoFilter(channel, video):
  return True


youtube.addVideosToPlaylist(
  'Subscription Feed',
  'My subscribed videos',
  datetime(2018, 10, 19),
  '~/.youtube-subscriptions-history',
  lambda channel: channelFilter(channel),
  lambda channel, video: videoFilter(channel, video))
