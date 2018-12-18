#!/usr/bin/env python

"""
Generate Anki deck for vocabulary.
"""

import genanki
import glob
import re
import sys
import toml
import unittest
from argparse import ArgumentParser
from collections import OrderedDict
from toml.decoder import TomlDecoder
from toml.encoder import TomlEncoder

OUTPUT_FILENAME = 'kanji_card_deck_output.apkg'

# use random.randrange(1 << 30, 1 << 31) to generate a suitable model_id,
# and hardcode it into your Model definition.

KANJI_CARD_DECK = genanki.Deck(
  2000001234, # XXX: DO NOT CHANGE
  'Generated Japanese') # XXX: DO NOT CHANGE

KANJI_CARD_MODEL = genanki.Model(
  2000001235, # XXX: DO NOT CHANGE
  'Generated Japanese Model', # The name of the model can change.
  fields=[
    # NB: Make changes to the Anki deck model fields using the
    # Anki interface first, or imports won't work as expected.
    {'name': 'Kanji'},
    {'name': 'Kana'},
    {'name': 'English'},
    {'name': 'Make Furigana Card?'},
    {'name': 'Make Kanji Card?'},
    {'name': 'Make Hiragana-only Card?'},
  ],
  # NB: Add or remove templates (with the same names) using the
  # Anki interface first, or imports won't work as expected.
  templates=[
    # Card 1 - Front: English; Back: English + Kanji + Kana
    {
      'name': 'English',
      'qfmt': '{{English}}',
      'afmt': '''
{{English}}

<hr id="answer">

<div>{{Kanji}}</div>
<div id="hint">{{Kana}}</div>
'''
    },
    # Card 2 (Optional) - Furigana (Kanji + Kana); Back: English + Kanji + Kana
    # This exists as an independent card instead of using doubly nested mustache
    # conditionals due to weirdness in Anki about not generating cards when imports
    # happen. This is the most clear-cut way to ensure card generation happens.
    # Something about doubly-nested if statements prevents Anki's bulk importing from
    # making such cards, even if they're non-blank. (They may only evaluate the first
    # level of if-statements during import...)
    {
      'name': 'Kanji + Kana',
      'qfmt': '''
{{#Make Furigana Card?}}
  <div>{{Kanji}}</div>
  <div id="hint">({{Kana}})</div>
{{/Make Furigana Card?}}
''',
      'afmt': '''
{{#Make Furigana Card?}}
  <div>{{Kanji}}</div>
  <div id="hint">({{Kana}})</div>
{{/Make Furigana Card?}}

<hr id="answer">

<div>{{English}}</div>
'''
    },
    # Card 3 (Optional) - Front: Kanji (only); Back: English + Kanji + Kana
    {
      'name': 'Kanji-only (optional)',
      'qfmt': '''
{{#Make Kanji Card?}}
  {{Kanji}}
{{/Make Kanji Card?}}
''',
      'afmt': '''
<div>{{Kanji}}</div>

<hr id="answer">

<div id="hint">({{Kana}})</div>

<div>{{English}}</div>
'''
    },
    # Card 3 (Optional) - Front: Hiragana (only); Back: English + Kanji + Kana
    {
      'name': 'Hiragana-only (optional)',
      'qfmt': '''
{{#Make Hiragana-only Card?}}
  {{Kana}}
{{/Make Hiragana-only Card?}}
''',
      'afmt': '''
<div>{{Kana}}</div>

<hr id="answer">

<div id="hint">({{Kanji}})</div>

<div>{{English}}</div>
'''
    },
  ],
  css = '''
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}

#hint {
  color: #00f;
}

#hint div {
  display: inline;
}
  ''')

class Note(genanki.Note):
  def __init__(self, verb_dict):
    self.kanji = verb_dict['kanji']
    self.kana = verb_dict['kana']
    self.english = verb_dict['english']
    self.level = verb_dict['level'] if 'level' in verb_dict else None
    self.tags = verb_dict['tags'] if 'tags' in verb_dict else []

    if self.level:
      self.tags.append(self.level)

    if 'make_kanji_card' in verb_dict and verb_dict['make_kanji_card']:
      self.make_kanji_card = 'y'
      self.make_furigana_card = ''
    else:
      self.make_kanji_card = ''
      self.make_furigana_card = 'y'

    if 'make_hiragana_only_card' in verb_dict and verb_dict['make_hiragana_only_card']:
      self.make_hiragana_only_card = 'y'
    else:
      self.make_hiragana_only_card = ''

    sort_field = self.kana

    # NB: Must match order of model.
    fields = [
      self.kanji,
      self.kana,
      self.english,
      self.make_furigana_card,
      self.make_kanji_card,
      self.make_hiragana_only_card,
    ]

    super().__init__(model=KANJI_CARD_MODEL,
        fields=fields,
        sort_field=self.kana,
        tags=self.tags,
        guid=None)

  @property
  def guid(self):
    return genanki.guid_for(self.kanji, self.kana)

  def card_count(self):
    if self.make_kanji_card == 'y':
      if self.make_hiragana_only_card == 'y':
        return 3
      else:
        return 2
    return 2

def read_vocabulary_notes(filename):
  with open(filename, 'r') as f:
    contents = f.read()
    toml_dict = toml.loads(contents)
    return toml_dict['cards']

total_notes = 0
total_cards = 0
total_disabled = 0
total_kanji_only = 0
total_hiragana_only = 0

for filename in glob.glob('**/*.toml', recursive=True):
  if 'cardgen' in filename:
    continue # XXX: Things here shouldn't be processed for now.
  print('Loading file: {0}'.format(filename))
  notes = read_vocabulary_notes(filename)
  for n in notes:
    if 'disabled' in n and n['disabled']:
      total_disabled += 1
      continue
    note = Note(n)
    if note.make_kanji_card:
      total_kanji_only += 1
    if note.make_hiragana_only_card:
      total_hiragana_only += 1
    KANJI_CARD_DECK.add_note(note)
    total_notes += 1
    total_cards += note.card_count()

print('Total cards: {0}'.format(total_cards))
print('Total notes: {0}'.format(total_notes))
print('  > notes disabled: {0}'.format(total_disabled))
print('  > notes /w kanji-only cards: {0}'.format(total_kanji_only))
print('  > notes w/ hiragana-only cards: {0}'.format(total_hiragana_only))
print('Output file: {0}'.format(OUTPUT_FILENAME))

genanki.Package(KANJI_CARD_DECK).write_to_file(OUTPUT_FILENAME)

