from youtube import YouTube, removePreviouslyHandledVideos
import datetime
from os.path import expanduser

youtube = YouTube()

playlistId = youtube.findOrCreatePlaylist('Subscription Feed', 'My subscribed videos, ')

publishedAfter = datetime.datetime(2018, 10, 16).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
videos = []

channels = youtube.getSubscriptionChannels()
for channel in channels:
  if channel.title != 'International Federation of Sport Climbing' and channel.title != 'USA Climbing':
    print("Reading channel: %s" % channel.title)
    youtube.addVideos(videos, channel.channelId, '', None, -1, publishedAfter)

removePreviouslyHandledVideos(videos, expanduser("~/.youtube-subscriptions-history"))

youtube.addToPlaylist(playlistId, sorted(videos, key=lambda video: video.publishedAt))
for video in sorted(videos, key=lambda video: video.publishedAt, reverse=True):
  print(video)
