#!/usr/bin/python
import os
from lxml import etree
import urllib
import urllib2

ROOT = 'http://profesoradunkley.weebly.com'


def get_files(page):
  parser = etree.HTMLParser()
  html = etree.parse(urllib2.urlopen(ROOT + page), parser)
  items = html.xpath('//a[contains(@class, "wsite-button")]')
  for i, item in enumerate(items):
    name = item[0].text.replace('/', '-')
    url = item.attrib['href']
    ext = os.path.splitext(url)[1]
    filename = '%02d %s%s' % (i + 1, name, ext)
    print('Downloading %s' % filename)
    urllib.urlretrieve(ROOT + url, filename)
    # print item.text + ''.join(etree.tostring(e) for e in item)


if __name__ == '__main__':
  # get_files('/powerpoints-de-gramaacutetica-avanzada.html')
  # get_files('/grammar-guides.html')
  get_files('/vocabulary-powerpoints.html')
