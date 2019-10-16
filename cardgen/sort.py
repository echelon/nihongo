#!/usr/bin/env python

"""
Sort entries into a well-defined order.
"""

import sys
import glob
import toml
from toml.encoder import TomlEncoder
from toml.decoder import TomlDecoder
from collections import OrderedDict

from library import INDEX_NAME
from library import NoteLibrary
from library import write_toml

skipped_count = 0

def sort_notes(note_toml_data):
  global skipped_count # TODO: Ugh. You monster.
  notes = []

  for note in note_toml_data[INDEX_NAME]:
    if 'tags' in note and note['tags']:
      note['tags'] = sorted(set(note['tags']))

    skip = False
    if 'kanji' not in note and 'kana' not in note:
      skip = True
    if 'kanji' in note and not note['kanji'].strip():
      skip = True
    if 'kana' in note and not note['kana'].strip():
      skip = True

    if skip:
      skipped_count += 1
      continue

    notes.append(note)

  notes = sorted(notes, key=lambda v: v['kana'].lstrip('～')) # Sort by kana, ignore '～'

  return { INDEX_NAME : notes }

def sort_set_file(filename):
  kanji = set()
  line_count = 0
  with open(filename, 'r') as f:
    for line in f:
      kanji.add(line.strip())
      line_count += 1

  kanji = sorted(kanji)
  unique_count = len(kanji)

  with open(filename, 'w') as f:
    for k in kanji:
      f.write('{}\n'.format(k))

  duplicate_characters = line_count - unique_count
  print('==== Sorted Set File {0} ==== '.format(filename))
  print('  Duplicate entries: {0}'.format(duplicate_characters))
  print('  Total unique entries: {0}'.format(unique_count))

def main():
  print('==== Notes files ==== ')
  total_notes = 0
  for filename in glob.glob('**/*.toml', recursive=True):
    if 'cardgen' in filename or 'temp/' in filename:
      continue # XXX: Things here shouldn't be processed for now.
    try:
      notes = NoteLibrary.read_notes_from_toml_file(filename)
      note_count = len(notes[INDEX_NAME])
      sorted_notes = sort_notes(notes)
      print('{0: <50} : {1} notes'.format(filename, note_count))
      write_toml(sorted_notes, filename)
      total_notes += note_count
    except Exception as e:
      print('Error processing file: {0}'.format(filename))
      print(e)

  print('==== Overall notes stats ====')
  print('  Skipped notes: {0}'.format(skipped_count))
  print('  Total notes: {0}'.format(total_notes))

  sort_set_file('config/kanji-only-vocab.txt')
  sort_set_file('config/suspended.txt')

if __name__ == '__main__':
    main()

