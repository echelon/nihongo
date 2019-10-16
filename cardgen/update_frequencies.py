#!/usr/bin/env python

"""
Update the entire set of notes with frequency data.
"""

import glob

from analysis import load_word_frequency_map
from library import INDEX_NAME
from library import NoteLibrary
from library import write_toml

def main():
  # Several { Word => frequency } maps.
  frequencies = {
    'anime_45k': load_word_frequency_map('lists/anime_45k_relevant_words.txt'),
    'leeds_15k' : load_word_frequency_map('lists/leeds_15k_frequency.txt'),
    'novel_3k' : load_word_frequency_map('lists/Japanese-Word-Frequency-List-1-3000.txt'),
    'wikipedia_10k' : load_word_frequency_map('lists/wikipedia_10k.txt'),
  }

  frequency_list_names = {
    'anime_45k': 'Anime 45k',
    'leeds_15k' : 'Leeds 15k',
    'novel_3k' : 'Novel 3k',
    'wikipedia_10k' : 'Wikipedia 10k',
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
        frequency_score = None
        frequency_list_name = None

        for freq_name, freq_map in frequencies.items():
          current_score = 1000000000
          if note['kanji'] in freq_map:
            current_score = freq_map[note['kanji']]
          elif note['kana'] in freq_map:
            current_score = freq_map[note['kana']]
          else:
            continue

          if not frequency_score \
              or current_score < frequency_score:
            frequency_score = current_score
            frequency_list_name = freq_name

        if frequency_list_name and frequency_score:
          list_name = frequency_list_names[frequency_list_name]
          note['highest_frequency'] = frequency_score
          note['highest_frequency_source'] = list_name
          freq_count += 1

      print('{0: <50} : {2} / {1} notes'.format(filename, note_count, freq_count))
      write_toml(notes, filename)

    except Exception as e:
      print('Error processing file: {0}'.format(filename))
      print(e)

if __name__ == '__main__':
    main()

