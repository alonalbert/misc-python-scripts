import httplib2
from datetime import datetime, date, timedelta
import json
import apiclient
from os.path import expanduser
from unidecode import unidecode

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

LAST_RUN = 'lastRun'
VIDEOS = 'videos'

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
    expire = self.__getOauthExpire()
    if credentials is None or credentials.invalid or datetime.now() > expire:
      flags = argparser.parse_args()
      credentials = run_flow(flow, storage, flags)
      expire = datetime.now() + timedelta(seconds=(credentials.token_response["expires_in"]))
      with open(OAUTH_EXPIRES_FILE, 'w') as file:
        file.write(expire.strftime('%Y-%m-%d %H:%M:%S.%f'))
    self.client = apiclient.discovery.build(SERVICE_NAME, API_VERSION, http=credentials.authorize(httplib2.Http()))

  def __getOauthExpire(self):
    try:
      with open(OAUTH_EXPIRES_FILE, 'r') as file:
        return datetime.strptime(file.read().replace('\n', ''), '%Y-%m-%d %H:%M:%S.%f')
    except:
      return datetime(1, 1, 1)

  def addVideosToPlaylist(self, playlistTitle, playlistDescription, publishedAfter, historyFilename, channelFilter, videoFilter):
    playlistId = self.__findOrCreatePlaylist(playlistTitle, playlistDescription)
    historyFilename = expanduser(historyFilename)
    history = self.__readHistoryFile(historyFilename, publishedAfter)

    publishedAfter = history[LAST_RUN]
    history[LAST_RUN] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    print('Adding videos publised after %s' % publishedAfter)
    channels = self.__getSubscriptionChannels()
    historyVideos = history[VIDEOS]
    historyVideosIds = set(map(lambda video: video['videoId'], historyVideos))

    allVideos = []
    for channel in channels:
      if channelFilter(channel):
        videos = self.__getNewVideos(channel, publishedAfter, historyVideosIds, videoFilter)
        print('Channel %s: %d new videos' % (channel.title, len(videos)))
        for video in videos:
          historyVideos.append(video.__dict__)
          allVideos.append(video)

    self.__addToPlaylist(playlistId, sorted(allVideos, key=lambda video: video.publishedAt))

    self.__writeHistoryFile(historyFilename, history)

  def __findOrCreatePlaylist(self, title, description):
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
    return response['id']

  def __readHistoryFile(self, filename, defaultPublishedAfter):
    try:
      with open(filename) as file:
        history = json.load(file)
    except:
      history = {
        LAST_RUN: defaultPublishedAfter.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        VIDEOS: []
      }
    return history

  def __writeHistoryFile(self, filename, history):
    history[VIDEOS] = sorted(history[VIDEOS], key=lambda video: video['publishedAt'])
    with open(filename, 'w') as file:
      json.dump(history, file, sort_keys=True, indent=2)

  def __getSubscriptionChannels(self):
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

  def __getNewVideos(self, channel, publishedAfter, historyVideos, filter):
    videos = []
    search = self.client.search()
    request = search.list(part='snippet', type='video', order='date', publishedAfter=publishedAfter,
                          channelId=channel.channelId)
    while request is not None:
      response = request.execute()
      items = response['items']
      for item in items:
        videoId = item['id']['videoId']
        snippet = item['snippet']
        title = snippet['title']
        publishedAt = snippet['publishedAt']
        channelTitle = snippet['channelTitle']
        video = Video(title, channelTitle, videoId, publishedAt)

        if videoId not in historyVideos and filter(channel, video):
          print('  Adding video %s' % title)
          videos.append(video)

      if len(items) == 0:
        # For some reason, if no items are returned, nextPage is always there.
        break
      request = search.list_next(request, response)
    return videos

  def __getPlaylistItems(self, playlistId):
    playlistItems = self.client.playlistItems()
    request = playlistItems.list(
      part='snippet,id',
      maxResults=50,
      playlistId=playlistId)
    videos = []
    while request is not None:
      response = request.execute()
      for item in response['items']:
        snippet = item['snippet']
        id = snippet["resourceId"]["videoId"]
        title = snippet['title']
        channelTitle = snippet['channelTitle']
        publishedAt = datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')

        videos.append(Video(title, channelTitle, id, publishedAt))
      request = playlistItems.list_next(request, response)
    return videos

  def __addToPlaylist(self, playlistId, videos):
    playlistItems = self.client.playlistItems()
    existingVideos = set(map(lambda video: video.videoId, self.__getPlaylistItems(playlistId)))

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
