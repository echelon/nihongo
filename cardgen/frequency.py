#!/usr/bin/env python

"""
Determine which frequent words are missing
"""

import argparse
import glob
import statistics
import string
import sys
import toml

from collections import OrderedDict
from toml.decoder import TomlDecoder
from toml.encoder import TomlEncoder

from constants import HIRAGANA
from constants import IGNORE_SYMBOLS
from constants import IGNORE_WORDS
from constants import KATAKANA

# I already have these words (perhaps a different politeness or kanji)
DUPLICATE_WORDS = set([
  'お祭り',
])

IGNORE_SET = set().union(HIRAGANA, KATAKANA, IGNORE_WORDS, IGNORE_SYMBOLS)

INDEX_NAME = 'cards'

def load_file_lines(filename):
  lines = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if line:
        lines.append(line)
  return lines

def load_word_frequency_map(filename):
  """
  Gets the {word => frequency} map in a file.
  Filters out comments and the ignore list of words.
  """
  words = load_file_lines(filename)
  return { word : rank for rank, word in enumerate(words) \
          if word not in IGNORE_WORDS \
          and word not in DUPLICATE_WORDS \
          and not word.startswith('#') }

def load_word_set(filename):
  """
  Load the word set in a file.
  Filters out comments and the ignore list of words.
  """
  word_set = set()
  words = load_file_lines(filename)
  for word in words:
    if word in IGNORE_WORDS \
        or word in DUPLICATE_WORDS \
        or word.startswith('#'):
      continue
    word_set.add(word)
  return word_set

class NoteLibrary:
  def __init__(self):
    self.notes = set()

  def check_in_library(self, word):
    if not self.notes:
      self.notes = self.load_library()
    return word in self.notes

  def load_library(self):
    if not self.notes:
      self.notes = self.do_load_library()

  @staticmethod
  def do_load_library():
    all_notes = NoteLibrary.import_all_notes()
    note_word_set = set()
    for note in all_notes:
      # NB: Words might be recorded as kanji or kana in frequency data
      note_word_set.add(note['kanji'])
      note_word_set.add(note['kana'])
      # Also get rid of characters we might not match on
      note_word_set.add(note['kanji'].replace('～', ''))
      note_word_set.add(note['kana'].replace('～', ''))
    return note_word_set

  @staticmethod
  def import_all_notes():
    all_notes = []
    for filename in glob.glob('**/*.toml', recursive=True):
      if 'cardgen' in filename or 'temp/' in filename:
        continue # XXX: Things here shouldn't be processed for now.
      try:
        notes = NoteLibrary.read_notes_from_toml_file(filename)
        notes = notes[INDEX_NAME]
        all_notes.extend(notes)
      except Exception as e:
        print('Error processing file: {0}'.format(filename))
        print(e)
    return all_notes

  @staticmethod
  def read_notes_from_toml_file(filename):
    # Maintain key ordering in each item
    decoder = TomlDecoder(_dict=OrderedDict)
    with open(filename, 'r') as f:
      contents = f.read()
      return toml.loads(contents, decoder=decoder)

class Reports:
  def __init__(self):
    self.note_library = NoteLibrary()
    self.note_library.load_library()

    # Word sets
    self.wanikani_vocab_set = load_word_set('lists/wanikani_vocab.txt') # Needs frequent rebuild
    self.wiktionary_n5 = load_word_set('lists/jlpt_n5_wiktionary.txt')
    self.wiktionary_n4 = load_word_set('lists/jlpt_n4_wiktionary.txt')
    self.wiktionary_n3 = load_word_set('lists/jlpt_n3_wiktionary.txt')

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

  def print_anime_not_in_anki(self):
    """
    Cumulative frequency points (a steep curve with a very long tail)
      24.99% -  # 29 (number of words needed)
      50.01% -  # 261
      60.01% -  # 572
      65.01% -  # 833
      70.00% -  # 1,210
      75.00% -  # 1,750
      80.00% -  # 2,568
      85.00% -  # 3,887
      90.00% -  # 6,224
      95.00% -  # 11,275
      98.00% -  # 18,928
    """
    word_frequencies = self.build_ordered_frequency_list('anime_45k')
    for word, frequency in word_frequencies[0:1210]:
      if word in IGNORE_SET:
        continue
      if word in self.note_library.notes:
        continue
      print(u'{:<5} : {}'.format(frequency, word))


def main():
  # TODO: This code is messy af
  reports = Reports()

  reports.print_anime_not_in_anki()
  return


  # TODO: Anime 250 list: https://owlcation.com/humanities/250-anime-japanese-words-phrases
  # TODO: 500 common verbs list: https://www.linguajunkie.com/japanese/japanese-verbs-list
  wp_10k_lookup = load_word_frequency_map('lists/wikipedia_10k.txt')
  f_3k_lookup  = load_word_frequency_map('lists/Japanese-Word-Frequency-List-1-3000.txt')

  # Not frequency lists
  kore_6k_lookup = load_word_frequency_map('lists/optimized_kore_frequency.txt') # Not frequency!
  wiktionary_n5 = load_word_frequency_map('lists/jlpt_n5_wiktionary.txt')
  wiktionary_n4 = load_word_frequency_map('lists/jlpt_n4_wiktionary.txt')
  wiktionary_n3 = load_word_frequency_map('lists/jlpt_n3_wiktionary.txt')
  wanikani_vocab = load_word_frequency_map('lists/wanikani_vocab.txt')

  for word in note_library.notes:
    if word in f_3k_lookup:
      del f_3k_lookup[word]
    if word in wp_10k_lookup:
      del wp_10k_lookup[word]
    if word in kore_6k_lookup:
      del kore_6k_lookup[word]
    if word in wiktionary_n5:
      del wiktionary_n5[word]
    if word in wiktionary_n4:
      del wiktionary_n4[word]
    if word in wiktionary_n3:
      del wiktionary_n3[word]
    if word in wanikani_vocab:
      del wanikani_vocab[word]

  # Wanikani most frequent
  filtered = {}
  for word, frequency in wp_10k_lookup.items():
    if word in wanikani_vocab:
      filtered[word] = frequency

  for k, v in filtered.items():
    print(k, v)

  if True:
    return

  print('\n\n==== 3k list ====\n')
  for k, v in f_3k_lookup.items():
    print(k, v)

  print('\n\n==== Wikipedia 10k list ====\n')
  for k, v in wp_10k_lookup.items():
    print(k, v)

  print('\n\n==== Both lists ====\n')
  common_frequency_set = set(wp_10k_lookup.keys()).intersection(set(f_3k_lookup.keys()))
  common_frequency = {}
  for word in common_frequency_set:
    avg_frequency = (f_3k_lookup[word] + wp_10k_lookup[word])/2.0
    common_frequency[word] = avg_frequency
  in_order = [(k, common_frequency[k]) for k in sorted(common_frequency, key=common_frequency.get)]
  for word, freq in in_order:
    print(word, freq)

  print('\n\n==== Reddit Kore 6k useful list ({}) ====\n'.format(len(kore_6k_lookup.items())))
  for k, v in kore_6k_lookup.items():
    print(k, v)

  print('\n\n==== JLPT N5 ({}) ====\n'.format(len(wiktionary_n5.items())))
  for word in wiktionary_n5.keys():
    print(word)

  print('\n\n==== JLPT N4 ({}) ====\n'.format(len(wiktionary_n4.items())))
  for word in wiktionary_n4.keys():
    print(word)

  print('\n\n==== JLPT N3 ({}) ====\n'.format(len(wiktionary_n3.items())))
  for word in wiktionary_n3.keys():
    print(word)

  print('\n\n==== Wanikani Vocab ({}) ====\n'.format(len(wanikani_vocab.items())))
  for word in wanikani_vocab.keys():
    print(word)

if __name__ == '__main__':
    main()

