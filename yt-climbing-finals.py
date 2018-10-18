#!/usr/bin/python
from youtube import YouTube, removePreviouslyHandledVideos
import datetime
from os.path import expanduser

youtube = YouTube()

IFSC_CHANNEL = 'UC2MGuhIaOP6YLpUx106kTQw'
USA_CLIMBING_CHANNEL = 'UCAthhtcB-Aa5yDg8ECTTqcA'

playlistId = youtube.findOrCreatePlaylist('Climbing Finals', 'Final round of climbing competitions')

publishedAfter = datetime.datetime(2018, 1, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
videos = []

youtube.addVideos(videos, IFSC_CHANNEL, 'Finals', "Semi|Youth|Speed|Paraclimbing|Highlights", 20, publishedAfter)
youtube.addVideos(videos, USA_CLIMBING_CHANNEL, '',
                  'Youth|Collegiate|Speed|Qualification|Semi|(On the Road)|(Road to)|Junior', 20, publishedAfter)

removePreviouslyHandledVideos(videos, expanduser("~/.youtube-climbing-finals-history"))

print "Adding to playlist"
youtube.addToPlaylist(playlistId, sorted(videos, key=lambda video: video.publishedAt))
print "Done"
