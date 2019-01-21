# coding=utf-8
from lxml import etree
import urllib2
import re
from youtube import YouTube

YT_RE = re.compile(r'.*/(.*)\?.*')
youtube = YouTube()


def create_playlist_for_section(section, name, description):
  ids = []

  links = section.xpath('.//a')
  for link in links:
    url = link.attrib['href']
    try:
      video_html = etree.parse(urllib2.urlopen(url), parser)
      video_frame = video_html.xpath('//iframe[contains(@src, "www.youtube.com")]')
      if len(video_frame) > 0:
        ids.append(YT_RE.sub(r'\1', video_frame[0].attrib['src']))
    except:
      pass

  playlist = youtube.findOrCreatePlaylist(name, description)
  for id in ids:
    youtube.addVideoToPlaylist(playlist, id)


parser = etree.HTMLParser()
videos_html = etree.parse(urllib2.urlopen('http://www.senorjordan.com/los-videos/'), parser)

sections = videos_html.xpath('//div[@class="post"]//ol')

create_playlist_for_section(sections[1], 'Señor Jordan Advanced', 'Advanced Spanish lessons')
