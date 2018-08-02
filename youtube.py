#!/usr/bin/python

import httplib2
import sys
import datetime
import json
import apiclient
from os.path import expanduser
from unidecode import unidecode

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

PLAYLIST_DESCRIPTION = "My subscribed videos"

PLAYLIST_NAME = "Subscription Feed"

CLIENT_SECRETS_FILE = expanduser("~/.youtube_client_secrets.json")

SCOPE = "https://www.googleapis.com/auth/youtube"
SERVICE_NAME = "youtube"
API_VERSION = "v3"


class Channel:
  def __init__(self, title, channelId):
    self.title = unidecode(title)
    self.channelId = channelId

  def __repr__(self):
    return u"%s %s" % (self.title, self.channelId)


class Video:
  def __init__(self, title, channelTitle, videoId, publishedAt):
    self.publishedAt = publishedAt
    self.videoId = videoId
    self.channelTitle = unidecode(channelTitle)
    self.title = unidecode(title)

  def __repr__(self):
    return u"%s %s %s %s" % (self.publishedAt, self.channelTitle, self.title, self.videoId)


class YouTube:
  def __init__(self):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, message="Missing secret file", scope=SCOPE)
    storage = Storage(expanduser("~/.youtube-oauth2.json"))
    credentials = storage.get()
    if credentials is None or credentials.invalid:
      flags = argparser.parse_args()
      credentials = run_flow(flow, storage, flags)
    self.client = apiclient.discovery.build(SERVICE_NAME, API_VERSION, http=credentials.authorize(httplib2.Http()))

  def getSubscriptionChannels(self):
    results = []
    subscriptions = self.client.subscriptions()
    request = subscriptions.list(part='snippet', mine=True)
    while request is not None:
      response = request.execute()

      for item in response['items']:
        snippet = item['snippet']
        title = snippet['title']
        channelId = snippet['resourceId']['channelId']
        results.append(Channel(title, channelId))

      request = subscriptions.list_next(request, response)
    return results

  def addVideos(self, videos, channelId, publishedAfter):
    search = self.client.search()
    request = search.list(part='snippet', type='video', order='date', publishedAfter=publishedAfter,
                          channelId=channelId)
    while request is not None:
      response = request.execute()
      for item in response['items']:
        id = item['id']
        snippet = item['snippet']
        publishedAt = datetime.datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        title = snippet['title']
        channelTitle = snippet['channelTitle']
        videoId = id['videoId']

        videos.append(Video(title, channelTitle, videoId, publishedAt))

      request = search.list_next(request, response)

  def getPlaylistId(self):
    # Find our playlist
    playlists = self.client.playlists()
    request = playlists.list(part='snippet,id', mine=True)
    while request is not None:
      response = request.execute()

      for item in response['items']:
        if item['snippet']['title'] == PLAYLIST_NAME:
          return item['id']
      request = playlists.list_next(request, response)

    response = self.client.playlists().insert(
      part="id",
      body=dict(
        snippet=dict(
          title=PLAYLIST_NAME,
          description=PLAYLIST_DESCRIPTION),
        status=dict(
          privacyStatus="private"))
    ).execute()
    return request[id]

  def addToPlaylist(self, playlistId, videos):
    playlistItems = self.client.playlistItems()
    for video in videos:
      playlistItems.insert(
        part='snippet',
        body=dict(
          snippet=dict(
            playlistId=playlistId,
            resourceId=dict(
              kind='youtube#video',
              videoId=video.videoId
            )))
      ).execute()

  def deleteWatched(self, playlistId):
    playlistItems = self.client.playlistItems()
    request = playlistItems.list(part='snippet,status', playlistId=playlistId)

    response = request.execute()
    printJson(response)


def printJson(response):
  print json.dumps(response, indent=4, sort_keys=True)


youtube = YouTube()

playlistId = youtube.getPlaylistId()

youtube.deleteWatched(playlistId)

publishedAfter = datetime.datetime(2018, 6, 20).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
videos = []

# channels = youtube.getSubscriptionChannels()
# for channel in channels:
#   print channel.title
#   youtube.addVideos(videos, channel.channelId, publishedAfter)
#
# youtube.addToPlaylist(playlistId, sorted(videos, key=lambda video: video.publishedAt))
# for video in sorted(videos, key=lambda video: video.publishedAt, reverse=True):
#   print(video)
