#!/usr/bin/env python
from pprint import PrettyPrinter
from anki_export import ApkgReader

pp = PrettyPrinter(indent=2)

with ApkgReader('anki_decks/japanese_words.apkg') as apkg:
  cards = apkg.export()
  pp.pprint(cards)
  pp.pprint(dir(cards))

