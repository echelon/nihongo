"""
Common utilities for managing the note library.
"""

import glob
import toml

from collections import OrderedDict
from toml.decoder import TomlDecoder
from toml.encoder import TomlEncoder

INDEX_NAME = 'cards'

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

