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

from update_frequencies import ANIME_FREQUENCY_SUBFIELD
from update_frequencies import FREQUENCY_FIELD
from update_frequencies import calculate_highest_frequency

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
    # Even additive changes MUST be made in Anki's UI first, or
    # you wind up with a new deck 'Generated Japanese Model-{hash}'
    {'name': 'Kanji'},
    {'name': 'Kana'},
    {'name': 'English'},
    {'name': 'Make Furigana Card?'},
    {'name': 'Make Kanji Card?'},
    {'name': 'Make Hiragana-only Card?'},
    {'name': 'Level'},
    {'name': 'Highest Frequency'},
    {'name': 'Highest Frequency Source'},
    {'name': 'Frequency Anime'},
  ],
  # NB: Add or remove templates (with the same names) using the
  # Anki interface first, or imports won't work as expected.
  templates=[
    # Card 1 - Front: English; Back: English + Kanji + Kana
    {
      'name': 'English',
      'qfmt': '''
{{English}}

<footer>
  <div class="level level-{{Level}}">{{Level}}</div>
  {{#Highest Frequency}}
    <div class="frequency">
      {{Highest Frequency}} ({{Highest Frequency Source}})
      {{#Frequency Anime}}
        <br />
        {{Frequency Anime}} (anime)
      {{/Frequency Anime}}
    </div>
  {{/Highest Frequency}}
</footer>
''',
      'afmt': '''
{{English}}

<hr id="answer">

<div>{{Kanji}}</div>
<div id="hint">{{Kana}}</div>

<footer>
  <div class="level level-{{Level}}">{{Level}}</div>
  {{#Highest Frequency}}
    <div class="frequency">
      {{Highest Frequency}} ({{Highest Frequency Source}})
      {{#Frequency Anime}}
        <br />
        {{Frequency Anime}} (anime)
      {{/Frequency Anime}}
    </div>
  {{/Highest Frequency}}
</footer>
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

  <footer>
    <div class="level level-{{Level}}">{{Level}}</div>
    {{#Highest Frequency}}
      <div class="frequency">
        {{Highest Frequency}} ({{Highest Frequency Source}})
        {{#Frequency Anime}}
          <br />
          {{Frequency Anime}} (anime)
        {{/Frequency Anime}}
      </div>
    {{/Highest Frequency}}
  </footer>
{{/Make Furigana Card?}}
''',
      'afmt': '''
{{#Make Furigana Card?}}
  <div>{{Kanji}}</div>
  <div id="hint">({{Kana}})</div>
{{/Make Furigana Card?}}

<hr id="answer">

<div>{{English}}</div>

<footer>
  <div class="level level-{{Level}}">{{Level}}</div>
  {{#Highest Frequency}}
    <div class="frequency">
      {{Highest Frequency}} ({{Highest Frequency Source}})
      {{#Frequency Anime}}
        <br />
        {{Frequency Anime}} (anime)
      {{/Frequency Anime}}
    </div>
  {{/Highest Frequency}}
</footer>
'''
    },
    # Card 3 (Optional) - Front: Kanji (only); Back: English + Kanji + Kana
    {
      'name': 'Kanji-only (optional)',
      'qfmt': '''
{{#Make Kanji Card?}}
  {{Kanji}}

  <footer>
    <div class="level level-{{Level}}">{{Level}}</div>
    {{#Highest Frequency}}
      <div class="frequency">
        {{Highest Frequency}} ({{Highest Frequency Source}})
        {{#Frequency Anime}}
          <br />
          {{Frequency Anime}} (anime)
        {{/Frequency Anime}}
      </div>
    {{/Highest Frequency}}
  </footer>
{{/Make Kanji Card?}}
''',
      'afmt': '''
<div>{{Kanji}}</div>

<hr id="answer">

<div id="hint">({{Kana}})</div>

<div>{{English}}</div>

<footer>
  <div class="level level-{{Level}}">{{Level}}</div>
  {{#Highest Frequency}}
    <div class="frequency">
      {{Highest Frequency}} ({{Highest Frequency Source}})
      {{#Frequency Anime}}
        <br />
        {{Frequency Anime}} (anime)
      {{/Frequency Anime}}
    </div>
  {{/Highest Frequency}}
</footer>
'''
    },
    # Card 3 (Optional) - Front: Hiragana (only); Back: English + Kanji + Kana
    {
      'name': 'Hiragana-only (optional)',
      'qfmt': '''
{{#Make Hiragana-only Card?}}
  {{Kana}}

  <footer>
    <div class="level level-{{Level}}">{{Level}}</div>
    {{#Highest Frequency}}
      <div class="frequency">
        {{Highest Frequency}} ({{Highest Frequency Source}})
        {{#Frequency Anime}}
          <br />
          {{Frequency Anime}} (anime)
        {{/Frequency Anime}}
      </div>
    {{/Highest Frequency}}
  </footer>
{{/Make Hiragana-only Card?}}
''',
      'afmt': '''
<div>{{Kana}}</div>

<hr id="answer">

<div id="hint">({{Kanji}})</div>

<div>{{English}}</div>

<footer>
  <div class="level level-{{Level}}">{{Level}}</div>
  {{#Highest Frequency}}
    <div class="frequency">
      {{Highest Frequency}} ({{Highest Frequency Source}})
      {{#Frequency Anime}}
        <br />
        {{Frequency Anime}} (anime)
      {{/Frequency Anime}}
    </div>
  {{/Highest Frequency}}
</footer>
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

footer {
  border-top: 1px dashed #888;
  color: #888;
  margin-top: 1em;
  padding-top: 0.3em;
}

.level {
  float: left;
}

.frequency {
  float: right;
  text-transform: capitalize;
}
  ''')

class Note(genanki.Note):
  def __init__(self, verb_dict, suspended=False):
    # These fields are always populated:
    self.kanji = verb_dict['kanji']
    self.kana = verb_dict['kana']
    self.english = verb_dict['english']
    # These fields are not always populated:
    self.level = verb_dict['level'] if 'level' in verb_dict else ''
    self.tags = verb_dict['tags'] if 'tags' in verb_dict else []
    self.frequency_highest = ''
    self.frequency_highest_source = ''
    self.frequency_anime = ''

    # Suspended notes will not show up for review until removed from suspension.
    self.suspended = suspended

    if self.level:
      self.tags.append(self.level)

    if self.suspended:
      # NB: This isn't functional, but helps manually searching for suspended cards.
      # At present, the 'suspended' scheduling does not work correctly to suspend cards.
      self.tags.append('suspended')
      self.tags.append('suspended_by_config')

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

    # TODO: Rename the Anki fields to frequency_* rather than highest_frequency_* to match
    # the new field naming scheme.
    if FREQUENCY_FIELD in verb_dict:
      frequency_data = verb_dict[FREQUENCY_FIELD]
      highest_frequency = calculate_highest_frequency(frequency_data)
      if highest_frequency:
        self.frequency_highest = str(highest_frequency['score'])
        self.frequency_highest_source = highest_frequency['source']
        # Only include additional anime frequency if it's not the highest
        if highest_frequency['source'] != ANIME_FREQUENCY_SUBFIELD \
            and ANIME_FREQUENCY_SUBFIELD in frequency_data:
          self.frequency_anime = str(frequency_data[ANIME_FREQUENCY_SUBFIELD])

    sort_field = self.kana

    # NB: Must match order of model.
    # Even additive changes MUST be made in Anki's UI first, or you wind up with a new
    # deck called 'Generated Japanese Model-{hash}'
    fields = [
      self.kanji,
      self.kana,
      self.english,
      self.make_furigana_card,
      self.make_kanji_card,
      self.make_hiragana_only_card,
      self.level,
      self.frequency_highest,
      self.frequency_highest_source,
      self.frequency_anime,
    ]

    super().__init__(model=KANJI_CARD_MODEL,
        fields=fields,
        sort_field=self.kana,
        tags=self.tags,
        guid=None)

  @property
  def guid(self):
    return genanki.guid_for(self.kanji, self.kana)

  @genanki.cached_property
  def cards(self):
    # We use cached_property instead of initializing in the constructor so that
    # the user can set the model after calling __init__ and it'll still work.
    rv = []
    for card_ord, any_or_all, required_field_ords in self.model._req:
      op = {'any': any, 'all': all}[any_or_all]
      if op(self.fields[ord_] for ord_ in required_field_ords):
        rv.append(genanki.Card(card_ord, suspend=self.suspended))
    return rv

  def card_count(self):
    if self.make_kanji_card == 'y':
      if self.make_hiragana_only_card == 'y':
        return 3
      else:
        return 2
    return 2

def read_set(filename):
  lines = []
  with open(filename, 'r') as f:
    lines = f.readlines()
    lines = map(lambda x: x.strip(), lines)
    lines = filter(None, lines)
  return set(lines)

KANJI_ONLY_VOCAB = read_set('config/kanji-only-vocab.txt')
SUSPENDED_VOCAB = read_set('config/suspended.txt')

def read_vocabulary_notes(filename):
  with open(filename, 'r') as f:
    contents = f.read()
    toml_dict = toml.loads(contents)
    return toml_dict['cards']

total_notes = 0
total_cards = 0
total_disabled = 0 # TODO: Deprecate and remove
total_suspended = 0
total_kanji_only = 0
total_hiragana_only = 0

for filename in glob.glob('**/*.toml', recursive=True):
  if 'cardgen' in filename or 'temp/' in filename:
    continue # XXX: Things here shouldn't be processed for now.
  print('Loading file: {0}'.format(filename))
  notes = read_vocabulary_notes(filename)
  for n in notes:
    if 'disabled' in n and n['disabled']:
      total_disabled += 1 # TODO: Deprecate and remove
      continue

    if 'kanji' not in n:
      raise Exception("Key 'kanji' not in note: {}".format(n))

    if n['kanji'] in KANJI_ONLY_VOCAB:
      n['make_kanji_card'] = True
      n['make_hiragana_only_card'] = False

    suspended = False
    if n['kanji'] in SUSPENDED_VOCAB:
      suspended = True
      total_suspended += 1

    note = Note(n, suspended=suspended)
    for card in note.cards:
      card.suspend = True

    if note.make_kanji_card:
      total_kanji_only += 1
    if note.make_hiragana_only_card:
      total_hiragana_only += 1

    KANJI_CARD_DECK.add_note(note)
    total_notes += 1
    total_cards += note.card_count()

print('Total cards: {0}'.format(total_cards))
print('Total notes: {0}'.format(total_notes))
print('  > notes disabled (deprecated): {0}'.format(total_disabled))
print('  > notes suspended: {0}'.format(total_suspended))
print('  > notes /w kanji-only cards: {0}'.format(total_kanji_only))
print('  > notes w/ hiragana-only cards: {0}'.format(total_hiragana_only))
print('Output file: {0}'.format(OUTPUT_FILENAME))

genanki.Package(KANJI_CARD_DECK).write_to_file(OUTPUT_FILENAME)

