日本語
======
My personal notes and tools for learning the Japanese language.

I'm also teaching my friends, so some of this will be structured to aid learning.

File Layout
-----------
- `/vocabulary` - toml files with a wide variety of annotated vocabulary. These
  will be updated frequently during study.

  Where possible, there will only be one English meaning provided for each
  Japanese word. This is to aid in memorizing and recalling synonyms.

  **Important Note:** From time to time I may change the English definitions of
  words. This will not change the card's UUID / hash, so SRS data will be retained.
  I'll also be moving vocabulary around and adjusting the tagging, but that should
  be entirely non-destructive.

- `/cardgen` - utilities for sorting and normalizing the vocabulary as well as
  tools to turn the vocabulary into Anki decks. The `sort.py` normalization utility
  should be run before any changes to vocab toml files are committed. This keeps the
  vocab files clean and consistent.

- `/config/kanji-only-vocab.txt` contains a newline-delimited set of vocab for which
  furigana hints are not desired. The Anki deck generation code reads in this file and
  will generate kanji-only cards for any vocab matching these entries in the 'kanji'
  field. If you don't wish to use these settings (or wish to adjust them), empty the
  file or adjust it per your preference. In the future such configuration files will be
  moved outside of version control.

There are other assorted files elsewhere in this repo, but it's mostly legacy garbage
that can be ignored. I'll be removing it and tidying things up as I have the time.

Installation
------------
The scripts here are written in Python 3. Dependencies are managed with `venv`.
Install a local venv, activate, and download dependencies as follows:

```python
python3 -m venv python
source python/bin/activate
pip install -r requirements.txt
```

Usage
-----
(It's extremely useful to understand the difference between Anki "cards" and "notes"
prior to reading this section. See their guide for details.)

Since the Anki deck generation code in this repository uses stable names and UUIDs for
the decks it generates, you can safely re-generate your decks and re-import them without
losing your SRS timing data. This is immensely useful when making changes to the
vocabulary (mutating, adding, or removing) or changing kanji-only configurations.

Each TOML entry in the `vocabulary` directory corresponds to an anki "note" and can have
several cards generated for it. The "kanji" and "kana" fields of the TOML vocabulary
entries are used to generate the note's UUID, so changes to any fields _other_ than these
two will allow the note and respective cards to retain their SRS history. If you change
the kanji or kana, however, all learning data will be lost and the entry will be treated
as new / unseen.

If you change the kanji-only / furigana settings for any note, it changes which cards are
generated for that note. This is because the generation code makes changes to the templates
that render the undesired cards "empty"; Anki does not generate empty cards. It's important
to mention, however, that Anki tries not to delete SRS data until you tell it. If you
previously studied a card that you later hide (eg. by switching a furigana card to
kanji-only), Anki will now show an "empty" front-facing card. To get rid of these (and
purge the respective SRS data for the cards), select `Tools -> Empty Cards` (in Linux - not
sure where this menu option lives for other OSes).

Card Templates
--------------

### For all vocab (except verbs)

```toml
[[cards]]
kanji = '' # Kanji. If gairaigo, katakana (which is also duplicated in kana for now).
kana = '' # Hiragana or katakana to function as furigana.
english = '' # English translation. Multiple definitions typically separated with ';'
source = '' # Where this vocabulary word originated from
level = 'n[1-5]' # JLPT level: n1, n2, n3, n4, n5. Omitted if not in JLPT.
explain = '' # Optional URL for further reading
tags = [] # grab bag of tags. 'common' is a tag used to denote frequent useage words
```

### For verbs

```toml
[[cards]]
kanji = '' # Kanji. If gairaigo, katakana (which is also duplicated in kana for now).
kana = '' # Hiragana or katakana to function as furigana.
english = ''# English translation. Multiple definitions typically separated with ';'. If transitive, there is a '~' present.
english-conjugated = { base = '', past = '', plural = '', continous = '' } # Conjugations
verb-type = '' # ichidan, godan-mu, godan-bu, etc.
transitive = false # whether the verb is transitive or not
level = 'n[1-5]' # JLPT level: n1, n2, n3, n4, n5. Omitted if not in JLPT.
explain = '' # Optional URL for further reading
tags = [] # grab bag of tags. 'common' is a tag used to denote frequent useage words
```

Learning Kanji
--------------
- 2136 Jouyou kanji (elementary and middle school)
  - 1006 taught in primary school (the kyouiku kanji)
  - 1130 taught in secondary school
  - 862 additional kanji allowed for person names (not in Jouyou)

- Wanikani is a useful SRS website that teaches:
  - Kanji: 2027
  - Vocab: 6287

JLPT
----

Levels

- n5: Basic. 800 vocab, 100 kanji. 150 hours of study.
  "Ability to understand some basic Japanese."
- n4: Elementary. 1.5k vocab, 300 kanji. 300 hours.
  "Ability to understand basic Japanese."
- n3: Intermediate. 3.7k vocab, 650 kanji. 450 hours.
  "Ability to understand Japanese used in everyday situations to a certain degree."
- n2: Pre-Advanced. 6k vocab, 1k kanji. 600 hours.
  "Ability to understand Japanese used in everyday situations, and in a variety of
  circumstances to a certain degree."
- n1: Advanced. 10k-18k vocab, 2k kanji. 900 hours.
  "The ability to understand Japanese used in a variety of circumstances."

### JLPT Links

- [JLPT vocabulary lists](https://jlptstudy.net/N5/)
- [Complete list of vocabulary for the JLPT N5](https://nihongoichiban.com/2011/04/30/complete-list-of-vocabulary-for-the-jlpt-n5/)
- [About the JLPT](http://www.tanos.co.uk/jlpt/aboutjlpt/)
- https://www.japanesewithanime.com/2016/10/koitsu-soitsu-aitsu-doitsu-meaning.html

Misc Links
-----

- [jisho.org: Japanese dictionary](https://jisho.org/)
- [Irasshai (Japanese I & II video lectures)](http://www.gpb.org/irasshai)
- [Anime subtitles in Japanese](http://kitsunekko.net/)

License
-------
Public domain.

