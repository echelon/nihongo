#!/usr/bin/env python

import genanki

# use random.randrange(1 << 30, 1 << 31) to generate a suitable model_id,
# and hardcode it into your Model definition.

KANJI_CARD_MODEL = genanki.Model(
  2000000001,
  'So Many Kanji',
  fields=[
    {'name': 'Kanji'},
    {'name': 'Kana'},
    {'name': 'English'},
    {'name': 'Make Kanji Card?'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Kanji}} {{Kana}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{English}}',
    },
  ])

DECK = genanki.Deck(
  2000000000,
  'Japanese Japanese')

# Generate notes

my_note = genanki.Note(
  model=KANJI_CARD_MODEL,
  fields=['Foo', 'Bar', 'Baz', ''],
  tags=['asdf'],
  guid=genanki.guid_for('Foo', 'Bar'))

DECK.add_note(my_note)

genanki.Package(DECK).write_to_file('output.apkg')

