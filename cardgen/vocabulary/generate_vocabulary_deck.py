#!/usr/bin/env python

"""
Generate Anki deck for vocabulary.
"""

import genanki
import re
import sys
import toml
import unittest
from argparse import ArgumentParser
from collections import OrderedDict
from toml.decoder import TomlDecoder
from toml.encoder import TomlEncoder

# use random.randrange(1 << 30, 1 << 31) to generate a suitable model_id,
# and hardcode it into your Model definition.

KANJI_CARD_DECK = genanki.Deck(
  2000001234, # XXX: DO NOT CHANGE
  'Generated Japanese Vocabulary Deck')

KANJI_CARD_MODEL = genanki.Model(
  2000001235, # XXX: DO NOT CHANGE
  'Generated Japanese Vocabulary Model',
  fields=[
    {'name': 'Kanji'},
    {'name': 'Kana'},
    {'name': 'English'},
    {'name': 'Make Kanji Card?'},
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
    # Card 2 - Front: Kanji OR Kanji+Kana; Back: English + Kanji + Kana
    {
      'name': 'Kanji + Kana',
      'qfmt': '''
{{#Make Kanji Card?}}
  {{Kana}}
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
    self.level = verb_dict['level']
    self.tags = verb_dict['tags']
    #self.make_kanji_card = 'y' if verb_dict['make_kanji_card'] else ''
    self.make_kanji_card = ''# TODO: FALSE UNTIL ALL CARDS EVALUATED

    sort_field = self.kana
    # Must match order of model.
    fields = [self.kanji, self.kana, self.english, self.make_kanji_card]

    super().__init__(model=KANJI_CARD_MODEL,
        fields=fields,
        sort_field=self.kana,
        tags=self.tags,
        guid=None)

  @property
  def guid(self):
    return genanki.guid_for(self.kanji, self.kana)


def read_vocabulary(filename):
  with open(filename, 'r') as f:
    contents = f.read()
    toml_dict = toml.loads(contents)
    return toml_dict['cards']

vocabulary = read_vocabulary('n5-vocab.toml')

#print(KANJI_CARD_MODEL.to_json(0, 0))

for vocab in vocabulary:
  note = Note(vocab)
  KANJI_CARD_DECK.add_note(note)

genanki.Package(KANJI_CARD_DECK).write_to_file('kanji_card_deck_output.apkg')

