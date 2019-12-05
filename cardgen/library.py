"""
Common utilities for managing the TOML note library.
"""

import glob
import sys
import toml

from toml.decoder import InlineTableDict

from collections import OrderedDict
from toml.decoder import TomlDecoder
from toml.encoder import TomlEncoder

INDEX_NAME = 'cards'

class DynamicInlineTableDict(dict, InlineTableDict):
  """
  Concrete implementation of a dictionary that will be encoded as an
  inline table in TOML. See the encoder library for details on how
  this is used.
  """
  pass

def write_toml(note_toml_data, filename):
  # Use inline tables
  encoder = CustomTomlEncoder(preserve=True)
  toml_contents = toml.dumps(note_toml_data, encoder=encoder)
  with open(filename, 'w') as f:
    f.write(toml_contents)

unicode = str

def _dump_str(v):
  """
  Function lifted and modified from original python toml library.
  This was cutomized to selectively switch the quote escaping. The
  upstream library code is broken.
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

  def add_notes_from_file(self, filename):
    """
    If we recently added or updated a file, (re)load its changes.
    This is only additive and will not remove any notes.
    """
    notes = NoteLibrary.read_notes_from_toml_file(filename)
    notes = notes[INDEX_NAME]
    NoteLibrary.add_notes_to_set(notes, self.notes)

  @staticmethod
  def do_load_library():
    all_notes = NoteLibrary.import_all_notes()
    note_word_set = set()
    NoteLibrary.add_notes_to_set(all_notes, note_word_set)
    return note_word_set

  @staticmethod
  def add_notes_to_set(notes, set_):
    for note in notes:
      # NB: Words might be recorded as kanji or kana in frequency data
      set_.add(note['kanji'])
      set_.add(note['kana'])
      # Also get rid of characters we might not match on
      set_.add(note['kanji'].replace('～', ''))
      set_.add(note['kana'].replace('～', ''))

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

