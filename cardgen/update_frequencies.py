#!/usr/bin/env python

"""
Update the entire set of notes with frequency data.
"""

import glob
from typing import Dict, Tuple

from analysis import load_word_frequency_map
from library import DynamicInlineTableDict
from library import INDEX_NAME
from library import NoteLibrary
from library import write_toml

# Where we store the frequency data in our notes
FREQUENCY_FIELD = 'frequency_scores'
ANIME_FREQUENCY_SUBFIELD = 'anime'

# TODO: Remove after running migrations
DEPRECATED_FIELDS = [
  'frequency_highest',
  'frequency_highest_source',
  'highest_frequency',
  'highest_frequency_source',
]

def calculate_highest_frequency(frequency_data: Dict[str, int]) -> Dict[str, int]:
  """
  From a source->score dict, find the lowest score (highest frequency) source-score pair.
  """
  if not frequency_data:
    return None
  lowest_score = 1000000000
  lowest_score_source = None
  for source, score in frequency_data.items():
    if score < lowest_score:
      lowest_score = score
      lowest_score_source = source
  if not lowest_score_source:
    return None
  return {'source': lowest_score_source, 'score': lowest_score}

def main():
  # Several { Word => frequency } maps.
  frequencies = {
    'anime_45k': load_word_frequency_map('lists/anime_45k_relevant_words.txt'),
    'leeds_15k' : load_word_frequency_map('lists/leeds_15k_frequency.txt'),
    'novel_3k' : load_word_frequency_map('lists/Japanese-Word-Frequency-List-1-3000.txt'),
    'wikipedia_10k' : load_word_frequency_map('lists/wikipedia_10k.txt'),
  }

  frequency_list_names = {
    'anime_45k': ANIME_FREQUENCY_SUBFIELD,
    'leeds_15k' : 'leeds',
    'novel_3k' : 'novels',
    'wikipedia_10k' : 'wikipedia',
  }

  print('==== Notes files ==== ')
  total_notes = 0
  for filename in glob.glob('**/*.toml', recursive=True):
    if 'cardgen' in filename or 'temp/' in filename:
      continue # XXX: Things here shouldn't be processed for now.
    try:
      notes = NoteLibrary.read_notes_from_toml_file(filename)
      note_count = len(notes[INDEX_NAME])
      freq_count = 0

      for note in notes[INDEX_NAME]:
        # First we clean the note of deprecated frequency fields.
        # These were fields that were renamed or discarded.
        for deprecated_field in DEPRECATED_FIELDS:
          note.pop(deprecated_field, None)

        # Now we attach all of the word frequencies we know about the note.
        frequency_scores = {}

        for freq_name, freq_map in frequencies.items():
          current_score = None
          if note['kanji'] in freq_map:
            current_score = freq_map[note['kanji']]
          elif note['kana'] in freq_map:
            current_score = freq_map[note['kana']]
          else:
            continue

          human_name = frequency_list_names[freq_name].lower()
          frequency_scores[human_name] = current_score

        if frequency_scores:
          note[FREQUENCY_FIELD] = DynamicInlineTableDict(frequency_scores)
          freq_count += 1

      print('{0: <50} : {2} / {1} notes'.format(filename, note_count, freq_count))
      write_toml(notes, filename)

    except Exception as e:
      print('Error processing file: {0}'.format(filename))
      print(e)

if __name__ == '__main__':
    main()

