#!/usr/bin/env python

"""
Determine which frequent words are missing
"""

import sys
import glob
import toml
from toml.encoder import TomlEncoder
from toml.decoder import TomlDecoder
from collections import OrderedDict

IGNORE_WORDS = set([
 '\ufeffの', # Should probably just fix the list instead
 'あ',
 'う',
 'お',
 'か',
 'から',
 'く',
 'げ',
 'こ',
 'こと',
 'さ',
 'じゃ',
 'する',
 'せる',
 'そんな',
 'ぞ',
 'ため',
 'だ',
 'だけ',
 'って',
 'つ',
 'で',
 'です',
 'でも',
 'ど',
 'な',
 'など',
 'ぬ',
 'ね',
 'の',
 'のに',
 'ば',
 'へ',
 'ます',
 'まで',
 'も',
 'ら',
 'り',
 'る',
 'れる',
 'ろ',
 'わ',
 'を',
 'ん',
 'スる',
 'ド',
 'ン',
])

# I already have these words (perhaps a different politeness or kanji)
DUPLICATE_WORDS = Set.new([
  'お祭り',
])

INDEX_NAME = 'cards'

def get_file_lines(filename):
  lines = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if line:
        lines.append(line)
  return lines

def get_word_frequency_pairs(filename):
  """
  Gets the (word, frequency) tuples in a file.
  Filters out comments and the ignore list of words.
  """
  words = get_file_lines(filename)
  return { word : rank for rank, word in enumerate(words) \
          if word not in IGNORE_WORDS \
          and word not in DUPLICATE_WORDS \
          and not word.startswith('#') }

def read_notes_from_toml(filename):
  # Maintain key ordering in each item
  decoder = TomlDecoder(_dict=OrderedDict)
  with open(filename, 'r') as f:
    contents = f.read()
    return toml.loads(contents, decoder=decoder)

def read_all_notes():
  all_notes = []
  for filename in glob.glob('**/*.toml', recursive=True):
    if 'cardgen' in filename or 'temp/' in filename:
      continue # XXX: Things here shouldn't be processed for now.
    try:
      notes = read_notes_from_toml(filename)
      notes = notes[INDEX_NAME]
      all_notes.extend(notes)
    except Exception as e:
      print('Error processing file: {0}'.format(filename))
      print(e)
  return all_notes

def main():
  all_notes = read_all_notes()

  existing_words = set()
  for note in all_notes:
    # NB: Words might be recorded as kanji or kana in frequency data
    existing_words.add(note['kanji'])
    existing_words.add(note['kana'])

  # TODO: This code is messy af

  # TODO: Anime 250 list: https://owlcation.com/humanities/250-anime-japanese-words-phrases
  # TODO: 500 common verbs list: https://www.linguajunkie.com/japanese/japanese-verbs-list
  wp_10k_lookup = get_word_frequency_pairs('lists/wikipedia_10k.txt')
  f_3k_lookup  = get_word_frequency_pairs('lists/Japanese-Word-Frequency-List-1-3000.txt')

  # Not frequency lists
  kore_6k_lookup = get_word_frequency_pairs('lists/optimized_kore_frequency.txt') # Not frequency!
  wiktionary_n5 = get_word_frequency_pairs('lists/jlpt_n5_wiktionary.txt')
  wiktionary_n4 = get_word_frequency_pairs('lists/jlpt_n4_wiktionary.txt')
  wiktionary_n3 = get_word_frequency_pairs('lists/jlpt_n3_wiktionary.txt')
  wanikani_vocab = get_word_frequency_pairs('lists/wanikani_vocab.txt')

  for word in existing_words:
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

