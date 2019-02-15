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

- `/cardgen` - utilities for sorting and normalizing the vocabulary as well as
  tools to turn the vocabulary into Anki decks. The `sort` utility should be run
  before changes to vocab toml files are committed.

There are other files elsewhere, but it's mostly legacy garbage that can be ignored.
I'll be removing it and tidying things up when I have the time.

Installation
------------
The scripts here are written in Python 3. Dependencies are managed with `venv`.
Install a local venv, activate, and download dependencies as follows:

```python
python3 -m venv python
source python/bin/activate
pip install -r requirements.txt
```

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

