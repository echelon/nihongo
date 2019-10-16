"""
Common tools for flat file analysis.
"""

from constants import DUPLICATE_WORDS
from constants import HIRAGANA
from constants import IGNORE_MISC
from constants import IGNORE_SET
from constants import IGNORE_SYMBOLS
from constants import KATAKANA
from constants import OTHER_FORMS
from constants import PARTICLES

def load_file_lines(filename):
  lines = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if line:
        lines.append(line)
  return lines

def load_word_frequency_map(filename):
  """
  Gets the {word => frequency} map in a file.
  Filters out comments and the ignore list of words.
  """
  words = load_file_lines(filename)
  return { word : rank for rank, word in enumerate(words) \
          if word not in IGNORE_SET \
          and not word.startswith('#') }

def load_word_set(filename):
  """
  Load the word set in a file.
  Filters out comments and the ignore list of words.
  Splits lines with `/` into multiple words.
  """
  word_set = set()
  words = load_file_lines(filename)
  for word in words:
    if word in IGNORE_SET \
        or word in DUPLICATE_WORDS \
        or word.startswith('#'):
      continue
    word_list = word.split('/')
    word_list = [w.strip() for w in word_list]
    for w in word_list:
      word_set.add(w)
  return word_set

