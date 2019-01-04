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
  tools to turn the vocabulary into Anki decks.

There are other files elsewhere, but it's mostly legacy garbage that can be ignored.

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

```toml
[[cards]]
kanji = ''
kana = ''
english = ''
source = ''
make_kanji_card = true
hide_hiragana_card = true
level = 'n[1-5]'
tags = []
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

