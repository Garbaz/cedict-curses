# CEDICT Curses

Interactively analysing a Chinese sentence and look up words in the CC-CEDCIT dictionary.

![screenshot](Screenshot.png)

## Features

* Read sentence from clipboard or command-line argument
* Show Pinyin or [Zhuyin](https://en.wikipedia.org/wiki/Bopomofo) with tone colours for readings
* Add words to [Anki](https://apps.ankiweb.net/) (using [Anki Connect](https://foosoft.net/projects/anki-connect/))
  
## Requirements

* `curses`
* `cedict_utils`
* `dragonmapper`
* `pyperclip`
* `webbrowser`

The following command should do the trick:

```sh
python3 -m pip install cedict_utils dragonmapper pyperclip
```

(`curses` and `webbroser` should already be included with the python standard library)

## Usage

```sh
python3 cedict-curses.py [SENTENCE]

    SENTENCE - The initial sentence to load. Can be omitted.
```

Before starting, you'll have to download and extract [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cedict) into the folder of this program.


Inside the program you can use the following keys:

| Key   | Alt. Key | Function 
| ----- | -------- | --- 
| q     |          | Quit the program 
| SPACE |          | Load sentence from clipboard 
| RIGHT | l        | Move right in the sentence 
| LEFT  | h        | Move left in the sentence 
| DOWN  | j        | Select the next result 
| UP    | k        | Select the previous result 
| r     |          | Toggle between Pinyin and Zhuyin 
| a     | ENTER    | Add selected result to / show in Anki 
| f     | F1       | Search selected result on [forvo.com](https://forvo.com/) 

## Anki

1. Install [Anki Connect](https://ankiweb.net/shared/info/2055492159) addon for Anki.
2. In `settings.py`, set the `DECK`, `CARD_TYPE` and `WORD_FIELD` variables according to your Anki setup.
3. Press the `a` (or `ENTER`) key inside the program!

## Settings

In the `settings.py` file are a few variables to set, see the corresponding comments for more info.

## TODO

* Overflow handling. If there are too many results or the sentence is too long, things go bad...
* Comments, comments, comments
