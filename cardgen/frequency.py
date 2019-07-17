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

INDEX_NAME = 'cards'

def get_frequency_list(filename):
  frequency_list = []
  with open(filename, 'r') as f:
    for line in f:
      frequency_list.append(line.strip())
  return frequency_list

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

  wp_10k = get_frequency_list('lists/wikipedia_10k.txt')
  f_3k = get_frequency_list('lists/Japanese-Word-Frequency-List-1-3000.txt')

  wp_10k_lookup = { word : rank for rank, word in enumerate(wp_10k) }
  f_3k_lookup = { word : rank for rank, word in enumerate(f_3k) }

  for word in existing_words:
    if word in f_3k_lookup:
      del f_3k_lookup[word]
    if word in wp_10k_lookup:
      del wp_10k_lookup[word]

  print('==== 3k list ====')
  for k, v in f_3k_lookup.items():
    if k not in IGNORE_WORDS:
      print(k, v)

  print('==== Wikipedia 10k list ====')
  for k, v in wp_10k_lookup.items():
    if k not in IGNORE_WORDS:
      print(k, v)

if __name__ == '__main__':
    main()

