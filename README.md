# CEDICT Curses

Interactively analyze a Chinese sentence and look up words in the CC-CEDCIT dictionary.

![screenshot](Screenshot.png)

## Features

* Read sentence from clipboard or command-line argument
* Show Pinyin or [Zhuyin](https://en.wikipedia.org/wiki/Bopomofo) with tone colors for readings
* Add words to [Anki](https://apps.ankiweb.net/) (using [Anki Connect](https://foosoft.net/projects/anki-connect/))
  
## Requirements

* `curses`
* `cedict_utils`
* `dragonmapper`
* `pyperclip`

The following command should do the trick:

```sh
python3 -m pip install cedict_utils dragonmapper pyperclip
```

(`curses` should already be included with the python standard library)

## Usage

Before starting, you'll have to download and extract [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cedict) into the folder of this program.

```sh
python3 cedict-curses.py [SENTENCE]

    SENTENCE - The initial sentence to load. Can be omitted.
```

Inside the program you can use the following keys:

| Key | Function |
| --- | --- |
| q | Quit the program |
| SPACE | Load sentence from clipboard |
| RIGHT | Move right in the sentence |
| LEFT | Move left in the sentence |
| DOWN | Select the next result |
| UP | Select the previous result |
| r | Toggle between pinyin and zhuyin |
| a | Added selected result to / show in Anki |

## Anki

1. Install [Anki Connect](https://ankiweb.net/shared/info/2055492159) addon for Anki.
2. In `settings.py`, set the `DECK`, `CARD_TYPE` and `WORD_FIELD` variables according to your Anki setup.
3. Press the `a` key inside the program!

## Settings

In the `settings.py` file are a few variables to set, see the corresponding comments for more info.

## TODO

* Overflow handling. If there are too many results or the sentence is too long, curses simply crashes...
* Comments, comments, comments