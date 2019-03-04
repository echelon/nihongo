#!/usr/bin/env python

"""
Insert blank notes at the top of every set of cards.

Useful for creating new cards in bulk with an editor. 

This is undone by running the normalization code, `sort.py`.
"""

import glob
from collections import OrderedDict

from toml.decoder import InlineTableDict

from sort import read_notes_from_toml
from sort import write_toml
from sort import INDEX_NAME

class DynamicInlineTableDict(dict, InlineTableDict):
  """
  Concrete implementation of a dictionary that will be encoded as an
  inline table in TOML. See the encoder library for details on how
  this is used.
  """
  pass

def insert_blanks(notes, filename):
  blank_note = OrderedDict()
  keys = [
    ('kanji', ''),
    ('kana', ''),
    ('english', ''),
  ]

  if 'verbs' in filename:
    conjugated = OrderedDict([
      ('base', ''),
      ('past', ''),
      ('plural', ''),
      ('continuous', ''),
    ])

    conjugated = DynamicInlineTableDict(conjugated)

    keys.extend([
      ('english-conjugated', conjugated),
      ('verb-type', ''),
      ('transitive', False),
    ])

  keys.extend([
    ('source', ''),
    ('level', ''),
    ('explain', ''),
    ('tags', []),
  ])

  blank_note['source'] = ''
  blank_note['level'] = ''
  blank_note['explain'] = ''
  blank_note['tags'] = []

  blank_note = OrderedDict(keys)
  notes[INDEX_NAME].insert(0, blank_note)

def main():
  for filename in glob.glob('**/*.toml', recursive=True):
    print('Processing file: {0}'.format(filename))

    if 'cardgen' in filename or 'temp/' in filename:
      continue # XXX: Things here shouldn't be processed for now.

    try:
      notes = read_notes_from_toml(filename)
      insert_blanks(notes, filename)
      write_toml(notes, filename)
    except Exception as e:
      print('Error processing file: {0}'.format(filename))
      print(e)

if __name__ == '__main__':
    main()

