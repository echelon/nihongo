HIRAGANA = set([
  'あ',
  'い',
  'う',
  'え',
  'お',
  'か',
  'き',
  'く',
  'け',
  'こ',
  'が',
  'ぎ',
  'ぐ',
  'げ',
  'ご',
  'さ',
  'し',
  'す',
  'せ',
  'そ',
  'ざ',
  'じ',
  'ず',
  'ぜ',
  'ぞ',
  'た',
  'ち',
  'つ',
  'て',
  'と',
  'だ',
  'ぢ',
  'づ',
  'で',
  'ど',
  'な',
  'に',
  'ぬ',
  'ね',
  'の',
  'は',
  'ひ',
  'ふ',
  'へ',
  'ほ',
  'ば',
  'び',
  'ぶ',
  'べ',
  'ぼ',
  'ぱ',
  'ぴ',
  'ぷ',
  'ぺ',
  'ぽ',
  'ま',
  'み',
  'む',
  'め',
  'も',
  'や',
  'ゆ',
  'よ',
  'ら',
  'り',
  'る',
  'れ',
  'ろ',
  'わ',
  'を',
  'ん',
])

KATAKANA = set([
  'ア',
  'イ',
  'ウ',
  'エ',
  'オ',
  'カ',
  'キ',
  'ク',
  'ケ',
  'コ',
  'ガ',
  'ギ',
  'グ',
  'ゲ',
  'ゴ',
  'サ',
  'シ',
  'ス',
  'セ',
  'ソ',
  'ザ',
  'ジ',
  'ズ',
  'ゼ',
  'ゾ',
  'タ',
  'チ',
  'ツ',
  'テ',
  'ト',
  'ダ',
  'ヂ',
  'ヅ',
  'デ',
  'ド',
  'ナ',
  'ニ',
  'ヌ',
  'ネ',
  'ノ',
  'ハ',
  'ヒ',
  'フ',
  'ヘ',
  'ホ',
  'バ',
  'ビ',
  'ブ',
  'ベ',
  'ボ',
  'パ',
  'ピ',
  'プ',
  'ペ',
  'ポ',
  'マ',
  'ミ',
  'ム',
  'メ',
  'モ',
  'ヤ',
  'ユ',
  'ヨ',
  'ラ',
  'リ',
  'ル',
  'レ',
  'ロ',
  'ワ',
  'ヲ',
  'ン',
])

PARTICLES = set([
 'から',
 'くん',
 'こと',
 'だけ',
 'でも',
 'など',
 'のに',
 'まで',
 'より',
])

IGNORE_SYMBOLS = set([
  '|',
  '…',
  '→',
  '■',
  '◆',
  '○',
  '●',
  '★',
  '☆',
  '「',
  '」',
  '『',
  '』',
  '【',
  '】',
  '〜',
  '・',
  '！',
  '％',
  '＆',
  '（',
  '）',
  '＊',
  '，',
  '．',
  '／',
  '：',
  '＜',
  '＝',
  '＞',
  '？',
  '＾',
])

# NB: Some particles, words, or segments that come up in frequency lists
# TODO: many of these are grammar points and deserve attention
IGNORE_MISC = set([
  'かも',
  'じゃ',
  'する',
  'せる',
  'そんな',
  'ため',
  'ちゃう',
  'って',
  'てる',
  'です',
  'なん',
  'ます',
  'ゆっくりと', # Should just have ゆっくり
  'れる',
  'オレ', # In anime frequency list
  'スる',
  'ダメ', # In anime frequency list
  'ド',
  'バカ', # In anime frequency list
  'ホント', # In anime freq
  'ン',
])

# Alternate kanji for the same words
OTHER_FORMS = set([
  'さ来年', # 再来年
  'とり肉', # 鳥肉
  '円い', # FIXME: 丸い, though technically the meanings differ
  '初め', # 始め
  '叔母さん', # 伯母さん
  '叔父', # 伯父
  '御飯', # ご飯
  '明い', # 明るい
  '昨夜', # 夕べ
  '曲る', # 曲がる
  '河', # 川
  '登る', # 上る
  '終る', # 終わる
  '観る', # 見る
  '貼る', # 張る
  '速い', # 早い
  '鶏肉', # 鳥肉
])


# All the things
IGNORE_SET = set().union(HIRAGANA, KATAKANA, PARTICLES, IGNORE_SYMBOLS, IGNORE_MISC, OTHER_FORMS)

# I already have these words (perhaps a different politeness or kanji)
DUPLICATE_WORDS = set([
  'お祭り',
  '昼御飯', # Less common
  '朝御飯', # Less common
])

