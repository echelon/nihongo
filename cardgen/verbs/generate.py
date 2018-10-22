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
  def __init__(self, verb_dict):
    self.group = verb_dict['group']
    self.level = verb_dict['level']
    self.kanji = verb_dict['kanji']
    self.kana = verb_dict['kana']
    self.english = verb_dict['english']

  def volitional_plain_kanji(self):
    return self._volitional_plain(self.kanji)

  def volitional_plain_kana(self):
    return self._volitional_plain(self.kana)

  def _volitional_plain(self, base):
    # deru (ichi) -> de-you, de-mashou
    # furu (g-ru) -> fu-rou, fu-rimashou
    # aruku (g-ku) -> aru-kou, aru-kimashou
    # au (g-u) -> a-ou, a-imashou
    # erabu (g-bu) -> era-bou, era-bimashou
    # dasu (g-su) -> da-sou, da-shimasou
    # utsu (g-tsu) -> u-tou, u-chimashou
    # yomu (g-mu) -> yo-mou
    # XXX/DANGER: THESE HAVE NOT BEEN CONFIRMED!
    if self.group == 'ichidan':
      return re.sub('る$', 'よう', base)
    if self.group == 'godan-bu':
      return re.sub('ぶ$', 'ぼう', base)
    if self.group == 'godan-gu':
      return re.sub('ぐ$', 'ごう', base)
    if self.group == 'godan-ku':
      return re.sub('く$', 'こう', base)
    if self.group == 'godan-mu':
      return re.sub('む$', 'もう', base)
    if self.group == 'godan-ru':
      return re.sub('る$', 'ろう', base)
    if self.group == 'godan-su':
      return re.sub('す$', 'そう', base)
    if self.group == 'godan-tsu':
      return re.sub('つ$', 'とう', base)
    if self.group == 'godan-u':
      return re.sub('う$', 'おう', base)

  def volitional_polite_kanji(self):
    pass

  def volitional_polite_kana(self):
    pass


for verb in verbs:
  verb = Verb(verb)
  print(verb.volitional_plain_kanji())
  print(verb.volitional_plain_kana())

