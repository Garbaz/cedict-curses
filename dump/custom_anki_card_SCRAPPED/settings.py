##### Anki Settings #####

"""
The name of the deck where to look for and add cards.
"""
DECK = ">中文<"

"""
The type of card to add in case no card was found.
"""
NOTE_TYPE = "Cedict Curses"

"""
The fields of the note type where to insert what part of the word.
If left as an empty string, the component will be skipped.

`FIELD_UNIQUE` has to be non-empty. It will be filled with a combination of
Simplified & Traditional & Pinyin to uniquely identify the note. This way
separate cards for different readings or alternate characters can be added.
"""
FIELD_UNIQUE = "Unique"
FIELD_SIMPLIFIED = "Simplified"
FIELD_SIMPLIFIED_COLOR = "Simplified (Color)"
FIELD_TRADITIONAL = "Traditional"
FIELD_TRADITIONAL_COLOR = "Traditional (Color)"
FIELD_ZHUYIN = "Zhuyin"
FIELD_PINYIN = "Pinyin"
FIELD_ENGLISH = "English"
FIELD_SOUND = "Sound"

"""
What text to pass to the TTS Engine.
Possible values:
    'simplified' | 'traditional' | 'pinyin' | 'zhuyin'

In the case of 'simplified' or 'traditional', it isn't guranteed that the
generated audio will be the desired reading of the word. However 'pinyin'
and 'zhuyin' will sound less natural. Pick your poison...
"""
TTS_SRC_STRING = 'simplified'

"""
Which language code to invoke the TTS Engine with.
Possible values:
    'zh' | 'zh-CN' | 'zh-TW'
"""
TTS_LANGUAGE = 'zh'

##### Other Settings #####

"""
Whether or not to show Zhuyin (aka Bopomofo) instead of Pinyin.
Can always be toggled in-program with the `r` key.
Values:
    False - Pinyin
    True  - Zhuyin
"""
DEFAULT_READING_ZHUYIN = True
