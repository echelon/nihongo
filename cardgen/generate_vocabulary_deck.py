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
    {'name': 'Kanji'},
    {'name': 'Kana'},
    {'name': 'English'},
    {'name': 'Make Kanji Card?'},
    {'name': 'Hide Hiragana-only Card?'},
  ],
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
    # Card 2 - Front: None OR Kana OR Kanji+Kana; Back: English + Kanji + Kana
    {
      'name': 'Kanji + Kana',
      'qfmt': '''
{{#Make Kanji Card?}}
{{^Hide Hiragana-only Card?}}
  {{Kana}}
{{/Hide Hiragana-only Card?}}
{{/Make Kanji Card?}}

{{^Make Kanji Card?}}
  <div>{{Kanji}}</div>
  <div id="hint">({{Kana}})</div>
{{/Make Kanji Card?}}
''',
      'afmt': '''
{{#Make Kanji Card?}}
  {{Kana}}
{{/Make Kanji Card?}}

{{^Make Kanji Card?}}
  <div>{{Kanji}}</div>
  <div id="hint">({{Kana}})</div>
{{/Make Kanji Card?}}

<hr id="answer">

{{#Make Kanji Card?}}
  <div id="hint">{{Kanji}}</div>
{{/Make Kanji Card?}}

{{^Make Kanji Card?}}
  <span id="nothing"></span>
{{/Make Kanji Card?}}

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
    else:
      self.make_kanji_card = ''

    if 'hide_hiragana_card' in verb_dict and verb_dict['hide_hiragana_card']:
      self.hide_hiragana_card = 'y'
    else:
      self.hide_hiragana_card= ''

    sort_field = self.kana

    # NB: Must match order of model.
    fields = [
      self.kanji,
      self.kana,
      self.english,
      self.make_kanji_card,
      self.hide_hiragana_card,
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
      if self.hide_hiragana_card == 'y':
        return 2
      else:
        return 3
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
total_hiragana_hidden = 0

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
    if note.hide_hiragana_card:
      total_hiragana_hidden += 1
    KANJI_CARD_DECK.add_note(note)
    total_notes += 1
    total_cards += note.card_count()

print('Total cards: {0}'.format(total_cards))
print('Total notes: {0}'.format(total_notes))
print('  > notes disabled: {0}'.format(total_disabled))
print('  > notes kanji-only: {0}'.format(total_kanji_only))
print('  > notes \'hiragana-only\' hidden: {0}'.format(total_hiragana_hidden))
print('Output file: {0}'.format(OUTPUT_FILENAME))

genanki.Package(KANJI_CARD_DECK).write_to_file(OUTPUT_FILENAME)

