#!/usr/bin/env python

"""
Generate Anki deck for verb conjugations.
"""

import glob
import re
import sys
import toml
import unittest
from argparse import ArgumentParser
from collections import OrderedDict
from toml.decoder import TomlDecoder
from toml.encoder import TomlEncoder

OUTPUT_FILENAME = 'verb_card_deck_output.apkg'

def read_verbs():
  def read_notes(filename):
    with open(filename, 'r') as f:
      contents = f.read()
      toml_dict = toml.loads(contents)
      return toml_dict['cards']

  all_notes = []
  for filename in glob.glob('vocabulary/verbs/*.toml', recursive=True):
    if 'cardgen' in filename or 'temp/' in filename:
      continue # XXX: Things here shouldn't be processed for now.
    print('Loading file: {0}'.format(filename))
    notes = read_notes(filename)
    for n in notes:
      if 'disabled' in n and n['disabled']:
        continue
      all_notes.append(n)
  return all_notes

verbs = read_verbs()

class Verb:
  # Godan Ending -> Masu Stem
  # 'u' -> 'i' sound
  GODAN_TO_MASU_STEM = {
    'う' : 'い',
    'く' : 'き',
    'ぐ' : 'ぎ',
    'す' : 'し',
    'つ' : 'ち',
    'ぬ' : 'に',
    'ぶ' : 'び',
    'む' : 'み',
    'る' : 'り',
  }

  # 'u' -> 'a' sound
  # Used for present indicative plain negative
  GODAN_TO_NAI = {
    'う' : 'わ', # exception!
    'く' : 'か',
    'ぐ' : 'が',
    'す' : 'さ',
    'つ' : 'た',
    'ぬ' : 'な',
    'ぶ' : 'ば',
    'む' : 'ま',
    'る' : 'ら', # godan-ru, not ichidan!
  }

  GODAN_TO_TE = {
    'う' : 'って',
    'く' : 'いて',
    'ぐ' : 'いで',
    'す' : 'して',
    'つ' : 'って',
    'ぬ' : 'んで',
    'ぶ' : 'んで',
    'む' : 'んで',
    'る' : 'って', # godan-ru, not ichidan!
  }

  GODAN_TO_TA = {
    'う' : 'った',
    'く' : 'いた',
    'ぐ' : 'いだ', # what
    'す' : 'した', # wow
    'つ' : 'った',
    'ぬ' : 'んだ',
    'ぶ' : 'んだ',
    'む' : 'んだ',
    'る' : 'った', # godan-ru, not ichidan!
  }

  GODAN_TO_PLAIN_VOLITIONAL = {
    'う' : 'おう',
    'く' : 'こう',
    'ぐ' : 'ごう',
    'す' : 'そう',
    'つ' : 'とう',
    'ぬ' : 'のう',
    'ぶ' : 'ぼう',
    'む' : 'もう',
    'る' : 'ろう', # godan-ru, not ichidan!
  }

  GODAN_TO_PLAIN_IMPERATIVE = {
    'う' : 'え',
    'く' : 'け',
    'ぐ' : 'げ',
    'す' : 'せ',
    'つ' : 'て',
    'ぬ' : 'ね',
    'ぶ' : 'べ',
    'む' : 'め',
    'る' : 'れ', # godan-ru, not ichidan!
  }

  def __init__(self, verb_dict):
    self.level = verb_dict['level'] if 'level' in verb_dict else None
    self.group = verb_dict['verb-type']
    self.kanji = verb_dict['kanji']
    self.kana = verb_dict['kana']

    english = {}
    if 'english-conjugated' in verb_dict:
      english = verb_dict['english-conjugated']

    self.english = english

  def present_indicative(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Present Indicative form.
    Means "[Verb]", "Will [Verb]", or "Don't/Won't [Verb]"
    """
    if polite:
      if positive:
        return self._masu(self.kanji) if kanji else self._masu(self.kana)
      else:
        return self._masen(self.kanji) if kanji else self._masen(self.kana)
    else:
      if positive:
        return self.kanji if kanji else self.kana
      else:
        return self._nai(self.kanji) if kanji else self._nai(self.kana)

  def presumptive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Presumptive form.
    Means "Will Probably [Verb]" or "Will Probably Not [Verb]"
    """
    verb = self.present_indicative(polite=False, positive=positive, kanji=kanji)
    suffix = "でしょう" if polite else "だろう"
    return verb + suffix

  def volitional(self, polite=False, kanji=False):
    """
    Return the verb in Volitional form.
    Means "Let's [Verb]". There is no negative.
    """
    verb = self.present_indicative(positive=True, polite=polite, kanji=kanji)
    if polite:
      return re.sub('ます$', 'ましょう', verb)
    else:
      if self.group == 'ichidan':
        return re.sub('る$', 'よう', verb)
      else:
        for godan_end, ending in Verb.GODAN_TO_PLAIN_VOLITIONAL.items():
          if verb.endswith(godan_end):
            return re.sub(godan_end + '$', ending, verb)

  def imperative(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Imperative form.
    Means "Do [Verb]!" or "Do Not [Verb]!"
    """
    if polite:
      if positive:
        base = self._te(kanji=kanji)
      else:
        # eg. aruku -> arukanai de kudasai
        verb = self.present_indicative(polite=False, positive=False, kanji=kanji)
        base = verb + 'で'
      return base + 'ください'
    else:
      if positive:
        verb = self.present_indicative(polite=polite, positive=positive, kanji=kanji)
        if self.group == 'ichidan':
          return re.sub('る$', 'ろ', verb)
        else:
          for godan_end, ending in Verb.GODAN_TO_PLAIN_IMPERATIVE.items():
            if verb.endswith(godan_end):
              return re.sub(godan_end + '$', ending, verb)
      else:
        dictionary = self.kanji if kanji else self.kana
        return dictionary + 'な'

  def past_indicative(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Past Indicative form.
    Means "[Verb]ed"/"Have [Verb]ed" or "Didn't [Verb]"/"Haven't [Verb]ed"
    """
    if polite:
      verb = self.present_indicative(polite=True, positive=positive, kanji=kanji)
      if positive:
        return re.sub('ます$', 'ました', verb)
      else:
        return verb + 'でした'
    else:
      if positive:
        return self._ta(kanji=kanji)
      else:
        verb = self.present_indicative(positive=False, polite=False, kanji=kanji)
        return re.sub('い$', 'かった', verb)

  def past_presumptive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Past Presumptive form.
    Means "Probably [Verb]ed" or "Probably Didn't [Verb]"
    """
    verb = self.past_indicative(polite=False, positive=positive, kanji=kanji)
    suffix = "でしょう" if polite else "だろう"
    return verb + suffix

  def present_progressive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Present Progressive form.
    Means "[Verb]ing" or  "Not [Verb]ing"
    """
    te_form_base = self._te(kanji=kanji)
    if polite:
      suffix = 'います' if positive else 'いません'
    else:
      suffix = 'いる' if positive else 'いない'
    return te_form_base + suffix

  def _masu(self, base):
    # TODO: Update to be called like _ta(kanji=False)
    replaced = None
    if self.group == 'ichidan':
      replaced = re.sub('る$', '', base)
    else:
      for godan_end, stem in Verb.GODAN_TO_MASU_STEM.items():
        if base.endswith(godan_end):
          regex = re.compile(godan_end + '$')
          replaced = regex.sub(stem, base)
          break
    if replaced:
      return replaced + 'ます'

  def _masen(self, base):
    # TODO: Update to be called like _ta(kanji=False)
    masu = self._masu(base)
    if masu:
      return re.sub('ます$', 'ません', masu)

  def _nai(self, base):
    # TODO: Update to be called like _ta(kanji=False)
    replaced = None
    if self.group == 'ichidan':
      replaced = re.sub('る$', '', base)
    else:
      for godan_end, nai in Verb.GODAN_TO_NAI.items():
        if base.endswith(godan_end):
          regex = re.compile(godan_end + '$')
          replaced = regex.sub(nai, base)
          break
    if replaced:
      return replaced + 'ない'

  def _te(self, kanji=False):
    base = self.kanji if kanji else self.kana
    if self.group == 'ichidan':
      return re.sub('る$', 'て', base)
    else:
      for godan_end, te_form in Verb.GODAN_TO_TE.items():
        if base.endswith(godan_end):
          return re.sub(godan_end + '$', te_form, base)

  def _ta(self, kanji=False):
    base = self.kanji if kanji else self.kana
    if self.group == 'ichidan':
      return re.sub('る$', 'た', base)
    else:
      for godan_end, te_form in Verb.GODAN_TO_TA.items():
        if base.endswith(godan_end):
          return re.sub(godan_end + '$', te_form, base)

VERB_HASH = { verb['kanji'] : Verb(verb) for verb in verbs }

class TestVerbConjugation(unittest.TestCase):

  def test_present_indicative(self):
    def v(verb, polite, positive, kanji):
      return VERB_HASH[verb].present_indicative(polite, positive, kanji)
    # Polite
    self.assertEqual(v('歩く', True, True, True), '歩きます')
    self.assertEqual(v('歩く', True, True, False), 'あるきます')
    self.assertEqual(v('歩く', True, False, True), '歩きません')
    self.assertEqual(v('歩く', True, False, False), 'あるきません')
    # Plain
    self.assertEqual(v('歩く', False, True, True), '歩く')
    self.assertEqual(v('歩く', False, True, False), 'あるく')
    self.assertEqual(v('歩く', False, False, True), '歩かない')
    self.assertEqual(v('歩く', False, False, False), 'あるかない')

  def test_imperative(self):
    def v(verb, polite, positive, kanji):
      return VERB_HASH[verb].imperative(polite, positive, kanji)
    # Polite
    self.assertEqual(v('見る', True, True, True), '見てください')
    self.assertEqual(v('見る', True, True, False), 'みてください')
    self.assertEqual(v('読む', True, False, True), '読まないでください')
    self.assertEqual(v('読む', True, False, False), 'よまないでください')
    # Plain
    self.assertEqual(v('見る', False, True, True), '見ろ')
    self.assertEqual(v('見る', False, True, False), 'みろ')
    self.assertEqual(v('読む', False, False, True), '読むな')
    self.assertEqual(v('読む', False, False, False), 'よむな')

  def test_past_indicative(self):
    def v(verb, polite, positive, kanji):
      return VERB_HASH[verb].past_indicative(polite, positive, kanji)
    # Polite
    self.assertEqual(v('読む', True, True, True), '読みました')
    self.assertEqual(v('読む', True, True, False), 'よみました')
    self.assertEqual(v('読む', True, False, True), '読みませんでした')
    self.assertEqual(v('読む', True, False, False), 'よみませんでした')
    # Plain
    self.assertEqual(v('読む', False, True, True), '読んだ')
    self.assertEqual(v('読む', False, True, False), 'よんだ')
    self.assertEqual(v('読む', False, False, True), '読まなかった')
    self.assertEqual(v('読む', False, False, False), 'よまなかった')

  def test_past_presumptive(self):
    def v(verb, polite, positive, kanji):
      return VERB_HASH[verb].past_presumptive(polite, positive, kanji)
    # Polite
    self.assertEqual(v('遊ぶ', True, True, True), '遊んだでしょう')
    self.assertEqual(v('遊ぶ', True, True, False), 'あそんだでしょう')
    self.assertEqual(v('遊ぶ', True, False, True), '遊ばなかったでしょう')
    self.assertEqual(v('遊ぶ', True, False, False), 'あそばなかったでしょう')
    # Plain
    self.assertEqual(v('遊ぶ', False, True, True), '遊んだだろう')
    self.assertEqual(v('遊ぶ', False, True, False), 'あそんだだろう')
    self.assertEqual(v('遊ぶ', False, False, True), '遊ばなかっただろう')
    self.assertEqual(v('遊ぶ', False, False, False), 'あそばなかっただろう')

  def test_present_progressive(self):
    def v(verb, polite, positive, kanji):
      return VERB_HASH[verb].present_progressive(polite, positive, kanji)
    # Polite
    self.assertEqual(v('泣く', True, True, True), '泣いています')
    self.assertEqual(v('泣く', True, True, False), 'ないています')
    self.assertEqual(v('近づく', True, False, True), '近づいていません')
    self.assertEqual(v('近づく', True, False, False), 'ちかづいていません')
    # Plain
    self.assertEqual(v('決める', False, True, True), '決めている')
    self.assertEqual(v('決める', False, True, False), 'きめている')
    self.assertEqual(v('打つ', False, False, True), '打っていない')
    self.assertEqual(v('打つ', False, False, False), 'うっていない')

def main():
  print('Printing verbs:')
  print(len(verbs))
  for verb in verbs:
    print('============')
    verb = Verb(verb)
    for i in range(8):
      polite = i//4 % 2 == 0
      positive = i//2 % 2 == 0
      kanji = i % 2 == 0
      print(verb.present_indicative(polite=polite, positive=positive, kanji=kanji))

    print()
    for i in range(8):
      polite = i//4 % 2 == 0
      positive = i//2 % 2 == 0
      kanji = i % 2 == 0
      print(verb.presumptive(polite=polite, positive=positive, kanji=kanji))

    print()
    for i in range(4):
      polite = i//2 % 2 == 0
      kanji = i % 2 == 0
      print(verb.volitional(polite=polite, kanji=kanji))

    print()
    for i in range(8):
      polite = i//4 % 2 == 0
      positive = i//2 % 2 == 0
      kanji = i % 2 == 0
      print(verb.imperative(polite=polite, positive=positive, kanji=kanji))

    print()
    for i in range(8):
      polite = i//4 % 2 == 0
      positive = i//2 % 2 == 0
      kanji = i % 2 == 0
      print(verb.past_indicative(polite=polite, positive=positive, kanji=kanji))

    print()
    for i in range(8):
      polite = i//4 % 2 == 0
      positive = i//2 % 2 == 0
      kanji = i % 2 == 0
      print(verb.past_presumptive(polite=polite, positive=positive, kanji=kanji))

    print()
    for i in range(8):
      polite = i//4 % 2 == 0
      positive = i//2 % 2 == 0
      kanji = i % 2 == 0
      print(verb.present_progressive(polite=polite, positive=positive, kanji=kanji))


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--test', help='run the unit tests', action="store_true")
  args = parser.parse_args()

  if args.test:
    sys.argv.remove('--test') # passed to unittest module and blows up
    unittest.main()
  else:
    main()

