#!/usr/bin/python

import os.path
import duolingo
from collections import defaultdict
import pprint
from unidecode import unidecode

def get_password():
  with open(os.path.expanduser('~/.duolingo-password')) as f:
    return f.read().strip()


class Duo:
  PRINT_KEYS = [
    'beginner',
    'bonus',
    'levels_finished',
    'mastered',
    'practice_recommended',
    'strength',
  ]

  def __init__(self, username, password):
    self.duo = duolingo.Duolingo(username, password)

  def words(self):
    vocabulary = self.duo.get_vocabulary('es')['vocab_overview']

    word_map = {
      1: [],
      2: [],
      3: [],
      4: [],
    }

    for word in vocabulary:
      word_map[word['strength_bars']].append(word)

    for level, words in word_map.iteritems():
      print '%s: %d' % (level, len(words))

    infinitives = defaultdict(lambda: defaultdict(list))

    for word in vocabulary:
      if word['pos'] == 'Verb':
        infinitives[word['infinitive']][word['strength_bars']].append(word)

    for infinitive, levels in sorted(infinitives.iteritems()):
      print(infinitive)
      for level, words in levels.iteritems():
        print('  Strength %d' % level)
        print('    '),
        for word in words:
          print(word['word_string'] + ' '),
        print

    print('Total infinitives: %d' % len(infinitives))


  def topics(self):
    pp = pprint.PrettyPrinter(indent=2)
    topics = self.duo.get_learned_skills('es')

    all_words = set([])
    for i, topic in enumerate(sorted(topics, cmp=lambda t1, t2: self._compare_topics(t1, t2))):
      # self.print_topic(i, topic)
      self.print_new_words(all_words, i, topic)

    # pp.pprint(topics[28])

  def print_topic(self, order, topic):
    print('%-4s: %s:' % (order, topic['title']))
    for key in self.PRINT_KEYS:
      print('  %s: %s' % (key, topic[key]))
    print('  words: %s' % map(lambda word: unidecode(word), topic['words']))
    print

  def print_new_words(self, all_words, order, topic):
    words = map(lambda word: unidecode(word), topic['words'])
    new_words = []
    old_words = []
    for word in words:
        if word not in all_words:
          new_words.append(word)
          all_words.add(word)
        else:
          old_words.append(word)
    print('%-4s: %s:' % (order, topic['title']))
    print('    Old words: %s:' % (old_words))
    print('    New words: %s:' % (new_words))


  def _compare_topics(self, t1, t2):
    result = t1['coords_y'] - t2['coords_y']

    return result if result != 0 else t1['coords_x'] - t2['coords_x']


duo = Duo('AlonAlbert', get_password())
# duo.words()
duo.topics()
