#!/usr/bin/env python

"""
Sort entries into a well-defined order.
"""

import glob
import toml
from toml.encoder import TomlEncoder
from toml.decoder import TomlDecoder
from collections import OrderedDict

INDEX_NAME = 'cards'

def read_toml(filename):
  # Maintain key ordering in each item
  decoder = TomlDecoder(_dict=OrderedDict)
  with open(filename, 'r') as f:
    contents = f.read()
    return toml.loads(contents, decoder=decoder)

def sort_notes(note_toml_data):
  notes = []
  for note in note_toml_data[INDEX_NAME]:
    notes.append(note)
  notes = sorted(notes, key=lambda v: v['kana']) # Sort by kana
  return { INDEX_NAME : notes }

def write_toml(note_toml_data, filename):
  # Use inline tables
  encoder = TomlEncoder(_dict=dict, preserve=True)
  toml_contents = toml.dumps(note_toml_data, encoder=encoder)
  with open(filename, 'w') as f:
    f.write(toml_contents)

for filename in glob.glob('**/*.toml', recursive=True):
  print('Processing file {0}'.format(filename))
  note_toml = read_toml(filename)
  verbs_toml = sort_notes(note_toml)
  write_toml(verbs_toml, filename)

