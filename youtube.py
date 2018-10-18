import httplib2
import re
from datetime import datetime, date, timedelta
import json
import apiclient
from os.path import expanduser
from unidecode import unidecode

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

OAUTH_EXPIRES_FILE = expanduser("~/.youtube-oauth2-expires")
OAUTH_STORAGE_FILE = expanduser('~/.youtube-oauth2.json')
CLIENT_SECRETS_FILE = expanduser("~/.youtube-client-secrets.json")

SCOPE = "https://www.googleapis.com/auth/youtube"
SERVICE_NAME = "youtube"
API_VERSION = "v3"


def printJson(response):
  print json.dumps(response, indent=4, sort_keys=True)

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
    storage = Storage(OAUTH_STORAGE_FILE)
    credentials = storage.get()
    expire = self.getOauthExpire()
    if credentials is None or credentials.invalid or datetime.now() > expire:
      flags = argparser.parse_args()
      credentials = run_flow(flow, storage, flags)
      expire = datetime.now() + timedelta(seconds=(credentials.token_response["expires_in"]))
      with open(OAUTH_EXPIRES_FILE, 'w') as file:
        file.write(expire.strftime('%Y-%m-%d %H:%M:%S.%f'))
    self.client = apiclient.discovery.build(SERVICE_NAME, API_VERSION, http=credentials.authorize(httplib2.Http()))

  def getOauthExpire(self):
    try:
      with open(OAUTH_EXPIRES_FILE, 'r') as file:
        return datetime.strptime(file.read().replace('\n', ''), '%Y-%m-%d %H:%M:%S.%f')
    except:
      return datetime(1, 1, 1)

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

  def addVideos(self, videos, channelId, query, exclude, maxResults, publishedAfter):
    count = 0
    search = self.client.search()
    request = search.list(part='snippet', type='video', order='date', q=query, publishedAfter=publishedAfter,
                          channelId=channelId)
    while request is not None:
      response = request.execute()
      for item in response['items']:
        id = item['id']
        snippet = item['snippet']
        publishedAt = datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        title = snippet['title']
        if exclude is not None and re.search(exclude, title) is not None:
          continue
        channelTitle = snippet['channelTitle']
        videoId = id['videoId']

        videos.append(Video(title, channelTitle, videoId, publishedAt))
        count += 1
        if maxResults > 0 and count >= maxResults:
          return

      request = search.list_next(request, response)

  def findOrCreatePlaylist(self, title, description):
    # Find our playlist
    playlists = self.client.playlists()
    request = playlists.list(part='snippet,id', mine=True)
    while request is not None:
      response = request.execute()

      for item in response['items']:
        if item['snippet']['title'] == title:
          return item['id']
      request = playlists.list_next(request, response)

    response = self.client.playlists().insert(
      part="snippet,status",
      body=dict(
        snippet=dict(
          title=title,
          description=description),
        status=dict(
          privacyStatus="private"))
    ).execute()
    return response[id]

  def getPlaylistItems(self, playlistId):
    playlistItems = self.client.playlistItems()
    request = playlistItems.list(
      part='snippet,id',
      maxResults=50,
      playlistId=playlistId)
    videos = []
    while request is not None:
      response = request.execute()
      for item in response['items']:
        id = item['id']
        snippet = item['snippet']
        title = snippet['title']
        channelTitle = snippet['channelTitle']
        publishedAt = datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')

        videos.append(Video(title, channelTitle, id, publishedAt))
      request = playlistItems.list_next(request, response)
    return videos

  def addToPlaylist(self, playlistId, videos):
    playlistItems = self.client.playlistItems()
    existingVideos = set(map(lambda video: video.videoId, videos))

    for video in videos:
      if video.videoId in existingVideos:
        print("%s exists" % video.title)
        existingVideos.remove(video.videoId)
        continue

      print "Adding %s" % video.title
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

    for video in existingVideos:
      print "Deleting %s" % video
      playlistItems.delete(id=video)

def removePreviouslyHandledVideos(videos, filename):
  try:
    with open(filename, 'r') as file:
      history = file.read().splitlines()
  except:
    history = []
  historySet = set(history)
  videos = [video for video in videos if not video.videoId in historySet]
  with open(filename, 'w') as file:
    file.writelines(map(lambda video: video.videoId + '\n', videos + history))
