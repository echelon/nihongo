日本語
======
My personal notes on the Japanese language.

I'm also teaching my friends, so some of this will be structured to aid learning.

Layout
------
- `/vocabulary` - toml files with a wide variety of annotated vocabulary. These
  will be updated frequently during study.

- `/cardgen` - utilities for sorting and normalizing the vocabulary as well as
  tools to turn the vocabulary into Anki decks.

There are other files elsewhere, but it's mostly legacy garbage.

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
level = 'n'
tags = []
```

Kanji
-----
- 2136 Jouyou kanji (elementary and middle school)
  - 1006 taught in primary school (the kyouiku kanji)
  - 1130 taught in secondary school
  - 862 additional kanji allowed for person names (not in Jouyou)

- Wanikani teaches:
  - Kanji: 2027
  - Vocab: 6287

JLPT
----

Levels

- n5: 800 vocab, 100 kanji. 150 hours of study. "Ability to understand some basic Japanese."
- n4: 1.5k vocab, 300 kanji. 300 hours of study.
- n3: 3.7k vocab, 650 kanji. 450 hours of study.
- n2: 6k vocab, 1k kanji. 600 hours of study.
- n1: 10k-18k vocab, 2k kanji. 900 hours of study. "Ability to read and understand anything."

### JLPT Links

- [JLPT vocabulary lists](https://jlptstudy.net/N5/)
- [Complete list of vocabulary for the JLPT N5](https://nihongoichiban.com/2011/04/30/complete-list-of-vocabulary-for-the-jlpt-n5/)
- [About the JLPT](http://www.tanos.co.uk/jlpt/aboutjlpt/)

Misc Links
-----

- [jisho.org: Japanese dictionary](https://jisho.org/)
- [Irasshai (Japanese I & II video lectures)](http://www.gpb.org/irasshai)
- [Anime subtitles in Japanese](http://kitsunekko.net/)

License
-------
Public domain.

