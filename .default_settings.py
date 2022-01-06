##### Anki Settings #####

"""
The name of the deck where to look for and add cards.
"""
DECK = "!新中文"

"""
The type of card to add in case no card was found.
"""
NOTE_TYPE = "New Chinese"

"""
Whether or not to "mark" (i.e. add the "marked" tag) the note.
Independent of whether a new note is created or not.
"""
MARK_NOTE = True

"""
Whether or not to open the Anki Browser with the note selected.
Independent of whether a new note is created or not.
"""
OPEN_BROWSER=True

"""
The fields of the note where to insert which component of the entry.
If left as an empty string, the component will be skipped.

`FIELD_UNIQUE` has to be non-empty. It will be filled with a combination of
Simplified & Traditional & Pinyin to uniquely identify the note. This way
separate cards for different readings or alternate characters can be added.
"""
FIELD_UNIQUE = "Unique"
FIELD_SIMPLIFIED = "Simplified"
FIELD_SIMPLIFIED_COLOR = ""
FIELD_TRADITIONAL = "Traditional"
FIELD_TRADITIONAL_COLOR = ""
FIELD_ZHUYIN = "Zhuyin"
FIELD_ZHUYIN_COLOR = ""
FIELD_PINYIN = "Pinyin"
FIELD_PINYIN_COLOR = ""
FIELD_PINYIN_NUMBERS = "Pinyin (Numbers)"
FIELD_ENGLISH = "English"

##### Other Settings #####

"""
Whether or not to show Zhuyin (aka Bopomofo) instead of Pinyin.
Can always be toggled in-program with the `r` key.
Values:
    False - Pinyin
    True  - Zhuyin
"""
DEFAULT_READING_ZHUYIN = True
