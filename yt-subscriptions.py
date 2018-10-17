from youtube import YouTube
import datetime

youtube = YouTube()

playlistId = youtube.findOrCreatePlaylist('Subscription Feed', 'My subscribed videos, ')

publishedAfter = datetime.datetime(2018, 9, 19).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
videos = []

channels = youtube.getSubscriptionChannels()
for channel in channels:
  if channel.title != 'IFSC Climbing World Championships' and channel.title != 'USA Climbing':
    youtube.addVideos(videos, channel.channelId, '', None, -1, publishedAfter)

youtube.addToPlaylist(playlistId, sorted(videos, key=lambda video: video.publishedAt))
for video in sorted(videos, key=lambda video: video.publishedAt, reverse=True):
  print(video)
