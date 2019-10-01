#!/usr/bin/env python

"""
Import a tsv file into a new vocab TOML file.
"""

import csv
import glob
import os

from collections import OrderedDict

from library import INDEX_NAME
from library import NoteLibrary
from sort import write_toml

def hydrate_note(row):
  kanji = row[0]
  kana = row[1]
  english = row[2]
  level = row[3]

  keys = [
    ('kanji', kanji),
    ('kana', kana),
    ('english', english),
    ('source', 'wiktionary'),
    ('level', level),
    ('tags', ['generated', 'tsv']),
  ]
  return OrderedDict(keys)

def tsv_to_toml_filename(filename):
  path = os.path.splitext(filename)[0]
  base = os.path.basename(path)
  return 'vocabulary/generated_{}.toml'.format(base)

def main():
  # Load existing library
  note_library = NoteLibrary()
  note_library.load_library()

  # Scan and convert the tsv files
  for filename in glob.glob('lists/*.tsv', recursive=True):
    notes = []
    with open(filename) as fd:
      rd = csv.reader(fd, delimiter='\t', quotechar='"')
      for row in rd:
        kanji = row[0]
        kana = row[1]
        if kanji in note_library.notes or kana in note_library.notes:
          continue
        note = hydrate_note(row)
        notes.append(note)

    toml = {}
    toml[INDEX_NAME] = notes

    new_filename = tsv_to_toml_filename(filename)
    print('Writing {} notes to {}'.format(len(notes), new_filename))
    write_toml(toml, new_filename)

if __name__ == '__main__':
    main()

