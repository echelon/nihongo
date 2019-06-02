#!/usr/bin/env python

"""
Generate Anki deck for verb conjugations.
"""

import genanki
import glob
import re
import sys
import toml
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

  # NB/NOTE: The 'ru' here is 'godan-ru', not 'ichidan'!
  # In the case of provisional verbs, it does not matter.
  ENDING_U_TO_E = {
    'う' : 'え',
    'く' : 'け',
    'ぐ' : 'げ',
    'す' : 'せ',
    'つ' : 'て',
    'ぬ' : 'ね',
    'ぶ' : 'べ',
    'む' : 'め',
    'る' : 'れ', # godan-ru
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
        return self._masu(kanji=kanji)
      else:
        return self._masen(kanji=kanji)
    else:
      if positive:
        return self.kanji if kanji else self.kana
      else:
        return self._nai(kanji=kanji)

  def english_present_indicative(self, positive=False):
    if positive:
      return 'will ' + self.english['base']
    else:
      return 'won\'t ' + self.english['base']

  def presumptive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Presumptive form.
    Means "Will Probably [Verb]" or "Will Probably Not [Verb]"
    """
    verb = self.present_indicative(polite=False, positive=positive, kanji=kanji)
    suffix = "でしょう" if polite else "だろう"
    return verb + suffix

  def english_presumptive(self, positive=False):
    if positive:
      return 'will probably ' + self.english['base']
    else:
      return 'probably won\'t ' + self.english['base']

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

  def english_volitional(self):
    return 'let\'s ' + self.english['base']

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
          for godan_end, ending in Verb.ENDING_U_TO_E.items():
            if verb.endswith(godan_end):
              return re.sub(godan_end + '$', ending, verb)
      else:
        dictionary = self.kanji if kanji else self.kana
        return dictionary + 'な'

  def english_imperative(self, positive=False):
    if positive:
      return 'do {}!'.format(self.english['base'])
    else:
      return 'don\'t {}!'.format(self.english['base'])

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

  def english_past_indicative(self, positive=False):
    if positive:
      return self.english['past']
    else:
      past = 'didn\'t {}'.format(self.english['base'])
      # fix bad grammar
      past = re.sub("didn't be\\b", "wasn't", past)
      return past

  def past_presumptive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Past Presumptive form.
    Means "Probably [Verb]ed" or "Probably Didn't [Verb]"
    """
    verb = self.past_indicative(polite=False, positive=positive, kanji=kanji)
    suffix = 'でしょう' if polite else 'だろう'
    return verb + suffix

  def english_past_presumptive(self, positive=False):
    if positive:
      past = 'probably {}'.format(self.english['past'])
      past = re.sub('probably was\\b', 'was probably', past) # better wording
      return past
    else:
      past = 'probably didn\'t {}'.format(self.english['base'])
      past = re.sub('didn\'t be\\b', 'wasn\'t', past) # fix bad grammar
      return past

  def present_progressive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Present Progressive form.
    Means "[Verb]ing" or "Not [Verb]ing"
    """
    te_form_base = self._te(kanji=kanji)
    if polite:
      suffix = 'います' if positive else 'いません'
    else:
      suffix = 'いる' if positive else 'いない'
    return te_form_base + suffix

  def english_present_progressive(self, positive=False):
    if positive:
      return self.english['continuous']
    else:
      return 'not {}'.format(self.english['continuous'])

  def past_progressive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Past Progressive form.
    Means "Was [Verb]ing" or "Wasn't [Verb]ing"
    """
    te_form_base = self._te(kanji=kanji)
    if polite:
      suffix = 'いました' if positive else 'いませんでした'
    else:
      suffix = 'いた' if positive else 'いなかった'
    return te_form_base + suffix

  def english_past_progressive(self, positive=False):
    if positive:
      return 'was {}'.format(self.english['continuous'])
    else:
      return 'wasn\'t {}'.format(self.english['continuous'])

  def provisional(self, positive=False, kanji=False):
    """
    Return the verb in Provisional form.
    Means "If One [Verb]" or "If One Does Not [Verb]"
    """
    if positive:
      verb = self.kanji if kanji else self.kana
      for before, after in Verb.ENDING_U_TO_E.items():
        if verb.endswith(before):
          base = re.sub(before + '$', after, verb)
          return base + 'ば'
    else:
      verb = self.present_indicative(polite=False, positive=False, kanji=kanji)
      return re.sub('い$', 'ければ', verb)

  def english_provisional(self, positive=False):
    # NB: Currently the same as english_conditional
    if positive:
      provisional = 'if one {}'.format(self.english['plural'])
      return re.sub('one are\\b', 'one is', provisional) # fix bad grammar
    else:
      provisional = 'if one doesn\'t {}'.format(self.english['base'])
      return re.sub('doesn\'t be\\b', 'isn\'t', provisional) # fix bad grammar

  def conditional(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Conditional form.
    Means "If One [Verb]" or "If One Does Not [Verb]"
    """
    base = self.past_indicative(polite=polite, positive=positive, kanji=kanji)
    return base + 'ら'

  def english_conditional(self, positive=False):
    # NB: Currently the same as english_provisional
    if positive:
      conditional= 'if one {}'.format(self.english['plural'])
      return re.sub('one are\\b', 'one is', conditional) # fix bad grammar
    else:
      conditional = 'if one doesn\'t {}'.format(self.english['base'])
      return re.sub('doesn\'t be\\b', 'isn\'t', conditional) # fix bad grammar

  def potential(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Potential form.
    Means "Can [Verb]" or "Cannot [Verb]"
    """
    verb = self.kanji if kanji else self.kana
    if self.group == 'ichidan':
      base = re.sub('る$', 'られ', verb)
    else:
      for before, after in Verb.ENDING_U_TO_E.items():
        if verb.endswith(before):
          base = re.sub(before + '$', after, verb)
          break
    if polite:
      return base + 'ます' if positive else base + 'ません'
    else:
      return base + 'る' if positive else base + 'ない'

  def english_potential(self, positive=False):
    if positive:
      return 'can {}'.format(self.english['base'])
    else:
      return 'can\'t {}'.format(self.english['base'])

  def causative(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Causative form.
    Means "Make or Let (Somebody) [Verb]" or "Not Make or Let (Somebody) [Verb]"
    """
    if self.group == 'ichidan':
      base = self.kanji if kanji else self.kana
      base = re.sub('る$', 'さ', base)
    else:
      nai_form = self._nai(kanji=kanji)
      base = re.sub('ない$', '', nai_form)
    if polite:
      suffix = 'せます' if positive else 'せません'
    else:
      suffix = 'せる' if positive else 'せない'
    return base + suffix

  def english_causative(self, positive=False):
    if positive:
      causative = 'make {}'.format(self.english['base'])
    else:
      causative = 'not make {}'.format(self.english['base'])
    return re.sub('\\sbe\\s', ' ', causative) # fix bad grammar

  def passive(self, polite=False, positive=False, kanji=False):
    """
    Return the verb in Passive form.
    Means "Be [Verb]" or "Not Be [Verb]"
    """
    if self.group == 'ichidan':
      base = self.kanji if kanji else self.kana
      base = re.sub('る$', 'ら', base)
    else:
      nai_form = self._nai(kanji=kanji)
      base = re.sub('ない$', '', nai_form)
    if polite:
      suffix = 'れます' if positive else 'れません'
    else:
      suffix = 'れる' if positive else 'れない'
    return base + suffix

  def english_passive(self, positive=False):
    if positive:
      passive = 'be {}'.format(self.english['past'])
      return re.sub('be was\\b', 'be', passive) # fix bad grammar
    else:
      passive = 'not be {}'.format(self.english['past'])
      return re.sub('be was\\b', 'be', passive) # fix bad grammar

  def _masu(self, kanji=False):
    base = self.kanji if kanji else self.kana
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

  def _masen(self, kanji=False):
    masu = self._masu(kanji=kanji)
    if masu:
      return re.sub('ます$', 'ません', masu)

  def _nai(self, kanji=False):
    base = self.kanji if kanji else self.kana
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

# use random.randrange(1 << 30, 1 << 31) to generate a suitable model_id,
# and hardcode it into your Model definition.

KANJI_CARD_DECK = genanki.Deck(
  2000002000, # XXX: DO NOT CHANGE
  'Generated Japanese Verb Conjugation') # XXX: DO NOT CHANGE

KANJI_CARD_MODEL = genanki.Model(
  2000002001, # XXX: DO NOT CHANGE
  'Generated Japanese Verb Conjugation Model', # The name of the model can change.
  fields=[
    # NB: Make changes to the Anki deck model fields using the
    # Anki interface first, or imports won't work as expected.
    {'name': 'base_kanji'},
    {'name': 'base_kana'},
    {'name': 'base_english'},
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

class Conjugation:
  def __init__(self, name, has_negative=True, has_polite=True):
    self.name = name
    self.has_negative = has_negative
    self.has_polite = has_polite

  def conjugation_name(self):
    return self.name.strip().lower().replace(' ', '_')

  # TODO: Test
  def field_names(self):
    # NB: DO NOT CHANGE THE ORDER. APPEND ONLY.
    # I have not tested this, but Anki has the potential to lose SRS data
    # or get cards/fields out of sync if the field numbers change. The
    # ordering here directly maps to field numberings.
    fields = []

    prefix = self.conjugation_name() + '_'

    fields.extend([
      prefix + 'plain_positive_kanji',
      prefix + 'plain_positive_kana',
    ])

    if self.has_negative:
      fields.extend([
        prefix + 'plain_negative_kanji',
        prefix + 'plain_negative_kana',
      ])

    if self.has_polite:
      fields.extend([
        prefix + 'polite_positive_kanji',
        prefix + 'polite_positive_kana',
      ])
      if self.has_negative:
        fields.extend([
          prefix + 'polite_negative_kanji',
          prefix + 'polite_negative_kana',
        ])

    return fields

  def map_verb_fields(self, verb):
    # NB: DO NOT CHANGE THE ORDER. APPEND ONLY.
    # I have not tested this, but Anki has the potential to lose SRS data
    # or get cards/fields out of sync if the field numbers change. The
    # ordering here directly maps to field numberings.
    field_values = []

    # TODO: Instead of having one monolithic class 'Verb', have a base class
    # and then subclasses that implement each conjugation's rules. Then we
    # don't need to dynamic dispatch, you can just call `conjugate(...)`.
    method_name = self.conjugation_name()
    method = getattr(verb, method_name)

    if self.has_polite:
      if self.has_negative:
        field_values.extend([
          method(polite=False, positive=True, kanji=True),
          method(polite=False, positive=True, kanji=False),
          method(polite=False, positive=False, kanji=True),
          method(polite=False, positive=False, kanji=False),
          method(polite=True, positive=True, kanji=True),
          method(polite=True, positive=True, kanji=False),
          method(polite=True, positive=False, kanji=True),
          method(polite=True, positive=False, kanji=False),
        ])
      else:
        field_values.extend([
          method(polite=False, kanji=True),
          method(polite=False, kanji=False),
          method(polite=True, kanji=True),
          method(polite=True, kanji=False),
        ])
    else:
      if self.has_negative:
        field_values.extend([
          method(positive=True, kanji=True),
          method(positive=True, kanji=False),
          method(positive=False, kanji=True),
          method(positive=False, kanji=False),
        ])
      else:
        field_values.extend([
          method(kanji=True),
          method(kanji=False),
        ])

    return field_values

# NB: DO NOT CHANGE THE ORDER. APPEND ONLY.
# I have not tested this, but Anki has the potential to lose SRS data
# or get cards/fields out of sync if the field numbers change. The
# ordering here directly maps to field numberings.
CONJUGATIONS = [
  Conjugation('Present Indicative'),
  Conjugation('Presumptive'),
  Conjugation('Volitional', has_negative=False),
  Conjugation('Imperative'),
  Conjugation('Past Indicative'),
  Conjugation('Past Presumptive'),
  Conjugation('Present Progressive'),
  Conjugation('Past Progressive'),
  Conjugation('Provisional', has_polite=False),
  Conjugation('Conditional'),
  Conjugation('Potential'),
  Conjugation('Causative'),
  Conjugation('Passive'),
]

class Note(genanki.Note):
  def __init__(self, verb):
    #self.kanji = verb_dict['kanji']
    #self.kana = verb_dict['kana']
    #self.english = verb_dict['english']
    #self.level = verb_dict['level'] if 'level' in verb_dict else None
    #self.tags = verb_dict['tags'] if 'tags' in verb_dict else []

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
      self.base_kanji,
      self.base_kana,
      self.base_english,
      self.level,
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

if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--test', help='run the unit tests', action="store_true")
  args = parser.parse_args()

  if args.test:
    from generate_verb_deck_tests import *

    sys.argv.remove('--test') # passed to unittest module and blows up
    unittest.main()
  else:
    main()

