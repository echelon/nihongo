#!/usr/bin/env python

"""
Put all of the entries in the `verbs.toml` in a well-defined
order.
"""

import toml
from toml.encoder import TomlEncoder
from toml.decoder import TomlDecoder
from collections import OrderedDict

def read_toml(filename):
  # Maintain key ordering in each item
  decoder = TomlDecoder(_dict=OrderedDict)
  with open(filename, 'r') as f:
    contents = f.read()
    return toml.loads(contents, decoder=decoder)

def sort_verbs(verbs_toml):
  verbs = []
  for verb in verbs_toml['verbs']:
    verbs.append(verb)
  verbs = sorted(verbs, key=lambda v: v['kana']) # Sort by kana
  return { 'verbs': verbs }

def write_toml(verbs_toml, filename):
  # Use inline tables
  encoder = TomlEncoder(_dict=dict, preserve=True)
  toml_contents = toml.dumps(verbs_toml, encoder=encoder)
  with open(filename, 'w') as f:
    f.write(toml_contents)

verbs_toml = read_toml('verbs.toml')
verbs_toml = sort_verbs(verbs_toml)
write_toml(verbs_toml, 'verbs.toml')

