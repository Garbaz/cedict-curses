# CEDICT Curses

Interactive analyzing of a Chinese sentence and looking up words in the CC-CEDCIT dictionary. With Pinyin, Zhuyin and tone colors.

## __Features__

* Read sentence from clipboard or command-line argument
* Show Pinyin or [Zhuyin](https://en.wikipedia.org/wiki/Bopomofo) with MDBG-style tone colours for readings
* Add words to [Anki](https://apps.ankiweb.net/) (using [Anki Connect](https://foosoft.net/projects/anki-connect/))
* Search/Open selected word in certain websites (See [keybinds](#usage))

![screenshot](Screenshot.png)
  
## __Requirements__

```sh
python3 -m pip install cedict_utils dragonmapper pyperclip
```

(All other libraries should already be included with the python standard library.)

## __Setup__

Download and extract the [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cedict) dictionary file into the folder of this program. You can at any time re-download and replace the file to update the dictionary.

When starting the program for the first time, it will create a `settings.py` file and prompt you to edit it.

If you want to use the Anki interface, make sure you have the [Anki Connect](https://ankiweb.net/shared/info/2055492159) addon installed in Anki and set the settings in `settings.py` according to your setup (deck, note type, field names). The default values are just what I use, so they won't work out out of the box.

## __Usage__

```sh
python3 cedict-curses.py [SENTENCE]

    SENTENCE - The initial sentence to load. Can be omitted.
```


Inside the program you can use the following keys:

| Key       | Alt. Key   | Function 
| --------- | ---------- | --- 
| q         | ESCAPE     | Quit the program 
| SPACE     |            | Load sentence from clipboard 
| RIGHT     | l          | Move right in the sentence 
| LEFT      | h          | Move left in the sentence 
| DOWN      | j          | Select the next result 
| UP        | k          | Select the previous result 
| r         |            | Toggle between Pinyin and Zhuyin 
| a         | ENTER      | Add selected result to / show in Anki
| l         | F1         | Search selected result on [LINE Dict](https://dict.naver.com/linedict/zhendict/dict.html#/cnen/home)
| f         | F2         | Search selected result on [Forvo](https://forvo.com) (Simplified)
| Shift + f | SHIFT + F2 | Search selected result on [Forvo](https://forvo.com) (Traditional)
| g         | F3         | Search selected result on [the Chinese Grammar Wiki](https://resources.allsetlearning.com/chinese/grammar/Main_Page)
| i         | F4         | Search selected result on [iCIBA](https://www.iciba.com)
| m         | F5         | Search selected result on [MDBG](https://www.mdbg.net/chinese/dictionary)
| t         | F6         | Search selected result on [Moedict (萌典)](https://moedict.tw)


* _The F1,F2,... keys are roughly based on the Alt+1,Alt+2,... keybinds of the [Zhongwen Browser Addon](https://github.com/cschiller/zhongwen#readme), so I don't confuse myself too much._
* _Forvo differentiates between simplified and traditional versions of words, hence the two keybinds. Though note that you'll get a mix of Mainland and Taiwan (and other) pronounciations in either case..._

## __TODO__

* Maybe a cleaner way to handle "too many results" (scrolling?)
* Google Cloud TTS intergration?
