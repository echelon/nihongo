#!/usr/bin/env python

"""
Generate Anki deck for verb conjugations.
"""

import re
import toml
from toml.encoder import TomlEncoder
from toml.decoder import TomlDecoder
from collections import OrderedDict

def read_verbs(filename):
  with open(filename, 'r') as f:
    contents = f.read()
    toml_dict = toml.loads(contents)
    return toml_dict['verbs']

verbs = read_verbs('verbs.toml')

class Verb:
  # Godan Ending -> Masu Stem
  # 'u' -> 'i' sound
  GODAN_TO_MASU_STEM = {
    'う' : 'い',
    'く' : 'き',
    'ぐ' : 'ぎ',
    'す' : 'し',
    'つ' : 'ち',
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
    'ぶ' : 'ば',
    'む' : 'ま',
    'る' : 'ら',
  }

  GODAN_TO_PLAIN_VOLITIONAL = {
    'ぶ' : 'ぼう',
    'ぐ' : 'ごう',
    'く' : 'こう',
    'む' : 'もう',
    'る' : 'ろう', # godan-ru, not ichidan!
    'す' : 'そう',
    'つ' : 'とう',
    'う' : 'おう',
  }

  def __init__(self, verb_dict):
    self.group = verb_dict['group']
    self.level = verb_dict['level']
    self.kanji = verb_dict['kanji']
    self.kana = verb_dict['kana']
    self.english = verb_dict['english']

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
    stem = self.present_indicative(polite=False, positive=positive, kanji=kanji)
    suffix = "でしょう" if polite else "だろう"
    return stem + suffix

  def volitional(self, polite=False, kanji=False):
    """
    Return the verb in Volitional form.
    Means "Let's [Verb]". There is no negative.
    """
    verb = self.present_indicative(positive=True, polite=polite, kanji=kanji)
    if polite:
      volitional_polite = 'ましょう'
      return re.sub('ます$', volitional_polite, verb)
    else:
      if self.group == 'ichidan':
        return re.sub('る$', 'よう', verb)
      else:
        for godan_end, ending in Verb.GODAN_TO_PLAIN_VOLITIONAL.items():
          if verb.endswith(godan_end):
            return re.sub(godan_end + '$', ending, verb)
            #regex = re.compile(godan_end + '$')
            #return regex.sub(verb, ending)

  def _masu(self, base):
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
    masu = self._masu(base)
    if masu:
      return re.sub('ます$', 'ません', masu)

  def _nai(self, base):
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

