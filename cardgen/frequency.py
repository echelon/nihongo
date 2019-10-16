#!/usr/bin/env python

"""
Determine which frequent words are missing
"""

import argparse
import glob
import statistics
import string
import sys

from analysis import load_word_frequency_map
from analysis import load_word_set
from constants import DUPLICATE_WORDS
from constants import HIRAGANA
from constants import IGNORE_MISC
from constants import IGNORE_SET
from constants import IGNORE_SYMBOLS
from constants import KATAKANA
from constants import OTHER_FORMS
from constants import PARTICLES
from library import NoteLibrary

class Reports:
  def __init__(self):
    self.note_library = NoteLibrary()
    self.note_library.load_library()

    # Word sets
    # TODO: Anime 250 list: https://owlcation.com/humanities/250-anime-japanese-words-phrases
    # TODO: 500 common verbs list: https://www.linguajunkie.com/japanese/japanese-verbs-list
    self.vocabulary_sets = {
      'jlpt_n5': load_word_set('lists/jlpt_n5_wiktionary.txt'),
      'jlpt_n4': load_word_set('lists/jlpt_n4_wiktionary.txt'),
      'jlpt_n3': load_word_set('lists/jlpt_n3_wiktionary.txt'),
      'wanikani': load_word_set('lists/wanikani_vocab.txt'),
    }

    # Word => frequency maps
    self.frequencies = {
      'anime_45k': load_word_frequency_map('lists/anime_45k_relevant_words.txt'),
      'leeds_15k' : load_word_frequency_map('lists/leeds_15k_frequency.txt'),
      'novel_3k' : load_word_frequency_map('lists/Japanese-Word-Frequency-List-1-3000.txt'),
      'wikipedia_10k' : load_word_frequency_map('lists/wikipedia_10k.txt'),
    }

    # Average frequency from all lists
    self.averaged_frequency = {}

  def build_ordered_frequency_list(self, list_name):
    if list_name not in self.frequencies:
      raise Exception('List {} not in frequency sets.'.format(list_name))
    unordered_list = []
    for word, frequency in self.frequencies[list_name].items():
      unordered_list.append((word, frequency))
    #sorted_tuples = sorted(unordered_list, key=lambda tup: tup[1])
    #return map(lambda tup: tup[0], sorted_tuples)
    return sorted(unordered_list, key=lambda tup: tup[1])

  def calculate_average_frequency(self):
    # NB: Mathematically, this is a lie.
    word_tally = {}
    for frequency_map in self.frequencies.values():
      for word, frequency in frequency_map.items():
        if word not in word_tally:
          word_tally[word] = []
        word_tally[word].append(frequency)

    # Unsorted (word,avg) tuples
    averaged_frequencies = []
    for word, frequencies in word_tally.items():
      if word in HIRAGANA \
          or word in KATAKANA \
          or word in IGNORE_WORDS \
          or word in IGNORE_SYMBOLS \
          or word in string.ascii_letters \
          or word in string.digits:
        continue
      avg = float(statistics.mean(frequencies))
      averaged_frequencies.append((word, avg))

    sorted_frequencies = sorted(averaged_frequencies, key=lambda tup: tup[1])

    for word, frequency in sorted_frequencies[0:500]:
      print(word, frequency)

    return word_tally

  def print_anime_not_in_anki(self, limit=None):
    """
    Cumulative frequency points (a steep curve with a very long tail)
      24.99% -  # 29 (number of words needed)
      50.01% -  # 261
      58.28% -  # 500
      60.01% -  # 572
      65.01% -  # 833
      67.46% -  # 1,000
      70.00% -  # 1,210
      72.91% -  # 1,500
      75.00% -  # 1,750
      76.78% -  # 2,000
      79.66% -  # 2,500
      80.00% -  # 2,568
      81.93% -  # 3,000
      85.00% -  # 3,887
      85.32% -  # 4,000
      87.78% -  # 5,000
      90.00% -  # 6,224
      95.00% -  # 11,275
      98.00% -  # 18,928
    """
    word_frequencies = self.build_ordered_frequency_list('anime_45k')
    for word, frequency in word_frequencies[0:limit]:
      if word in IGNORE_SET:
        continue
      if word in self.note_library.notes:
        continue
      print(u'{:<5} : {}'.format(frequency, word))

  def print_set_not_in_anki(self, set_name):
    if set_name not in self.vocabulary_sets:
      raise Exception('Set {} not in vocabulary sets.'.format(set_name))
    for word in self.vocabulary_sets[set_name]:
      if word in IGNORE_SET:
        continue
      if word in self.note_library.notes:
        continue
      print (word)

def main():
  import argparse

  parser = argparse.ArgumentParser(description='Stats on Anki notes')
  parser.add_argument('--jlpt', dest='jlpt', nargs='+', default=[],
      help='show JLPT vocab not in Anki (n5, n4, etc.)')
  parser.add_argument('--anime', dest='anime', action='store_true',
      help='show anime vocab not in Anki (ordered by frequency)')
  parser.add_argument('--wanikani', dest='wanikani', action='store_true',
      help='show Wanikani not in Anki (ordered by frequency)')
  parser.add_argument('--limit', dest='limit', type=int,
      help='limit the number of results')
  args = parser.parse_args()
  show_help = True

  reports = Reports()

  jlpt = {
    'n3': 'jlpt_n3',
    'n4': 'jlpt_n4',
    'n5': 'jlpt_n5',
  }

  if args.anime:
    reports.print_anime_not_in_anki(args.limit)
    show_help = False

  if args.wanikani:
    reports.print_set_not_in_anki('wanikani')
    show_help = False

  for n in args.jlpt:
    n = n.lower()
    if n in jlpt:
      reports.print_set_not_in_anki(jlpt[n])
      show_help = False

  if show_help:
    parser.print_help()

if __name__ == '__main__':
    main()

