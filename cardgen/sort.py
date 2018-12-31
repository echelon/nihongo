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

INDEX_NAME = 'cards'

unicode = str

def _dump_str(v):
  """
  Function lifted and modified from original python toml library.
  """
  if sys.version_info < (3,) and hasattr(v, 'decode') and isinstance(v, str):
    v = v.decode('utf-8')
  v = "%r" % v # NB: adds wrapping quotes
  if v[0] == 'u':
    v = v[1:]
  if v.startswith("'") or v.startswith('"'):
    v = v[1:-1]
  use_singlequote = "'" not in v
  if use_singlequote:
    v = v.replace('\\"', '"')
    v = v.replace("'", "\\'")
  else:
    v = v.replace("\\'", "'")
    v = v.replace('"', '\\"')
  v = v.split("\\x")
  while len(v) > 1:
    i = -1
    if not v[0]:
      v = v[1:]
    v[0] = v[0].replace("\\\\", "\\")
    # No, I don't know why != works and == breaks
    joinx = v[0][i] != "\\"
    while v[0][:i] and v[0][i] == "\\":
      joinx = not joinx
      i -= 1
    if joinx:
      joiner = "x"
    else:
      joiner = "u00"
    v = [v[0] + joiner + v[1]] + v[2:]
  if use_singlequote:
    return unicode("'" + v[0] + "'")
  else:
    return unicode('"' + v[0] + '"')

class CustomTomlEncoder(TomlEncoder):
  def __init__(self, preserve=True):
    super().__init__(_dict=dict, preserve=preserve)
    self.dump_funcs[str] = _dump_str
    self.dump_funcs[unicode] = _dump_str

  def dump_list(self, v):
    retval = ''
    for u in v:
      retval += "" + unicode(self.dump_value(u)) + ", "
    retval = retval[:-2]
    return '[{0}]'.format(retval)

def read_notes_from_toml(filename):
  # Maintain key ordering in each item
  decoder = TomlDecoder(_dict=OrderedDict)
  with open(filename, 'r') as f:
    contents = f.read()
    return toml.loads(contents, decoder=decoder)

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

def write_toml(note_toml_data, filename):
  # Use inline tables
  encoder = CustomTomlEncoder(preserve=True)
  toml_contents = toml.dumps(note_toml_data, encoder=encoder)
  with open(filename, 'w') as f:
    f.write(toml_contents)

total_notes = 0
for filename in glob.glob('**/*.toml', recursive=True):
  if 'cardgen' in filename:
    continue # XXX: Things here shouldn't be processed for now.
  try:
    notes = read_notes_from_toml(filename)
    note_count = len(notes[INDEX_NAME])
    sorted_notes = sort_notes(notes)
    print('{0: <50} : {1} notes'.format(filename, note_count))
    write_toml(sorted_notes, filename)
    total_notes += note_count
  except Exception as e:
    print('Error processing file: {0}'.format(filename))
    print(e)

print('Skipped notes: {0}'.format(skipped_count))
print('Total notes: {0}'.format(total_notes))

