#!/usr/bin/python
#
from sys import argv
from lxml import etree
from lxml.etree import _Comment


root = etree.parse(argv[1])
# root = xml.etree.ElementTree.parse(argv[1]).getroot()

children = list(root.iter())

i = 0
while i < len(children):
  child = children[i]
  if isinstance(child, _Comment):
    i += 1
    comment = child
    string = children[i]

    comment.getparent().remove(comment)
    string.attrib['description'] = comment.text
    string.text = '\n      '+ string.text + '\n  '
  i += 1

print(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
