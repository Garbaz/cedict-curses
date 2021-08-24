import curses
from logging import error
from sys import stderr, argv
from cedict_utils import cedict
from dragonmapper import transcriptions
import curses
import pyperclip
import webbrowser
import unicodedata
import os
import gzip
import zipfile
import shutil

from settings import *
from anki import anki

logfile = open("cedict-curses.log", 'w')

alternate_searches = {
    "0": "零", "０": "零",
    "1": "一", "１": "一",
    "2": "二", "２": "二",
    "3": "三", "３": "三",
    "4": "四", "４": "四",
    "5": "五", "５": "五",
    "6": "六", "６": "六",
    "7": "七", "７": "七",
    "8": "八", "８": "八",
    "9": "九", "９": "九"
}


def error_failed_to_read_dict():
    print("Could not find dictionary file 'cedict_1_0_ts_utf-8_mdbg.txt'. Please download CC-CEDICT from", file=stderr)
    print("https://www.mdbg.net/chinese/dictionary?page=cedict", file=stderr)
    print("and extract it in this folder.", file=stderr)
    exit(1)


parser = cedict.CedictParser()

# Try to load dictionary file.
# If the file isn't found, try to find other forms of the file and extract/rename.
try:
    parser.read_file("cedict_1_0_ts_utf-8_mdbg.txt")
except FileNotFoundError:
    try:
        os.rename("cedict_ts.u8", "cedict_1_0_ts_utf-8_mdbg.txt")
        print("Found 'cedict_ts.u8', renaming to 'cedict_1_0_ts_utf-8_mdbg.txt'.")
    except FileNotFoundError:
        try:
            with zipfile.ZipFile("cedict_1_0_ts_utf-8_mdbg.zip") as z:
                print("Found 'cedict_1_0_ts_utf-8_mdbg.zip', extracting...")
                z.extractall()
            os.rename("cedict_ts.u8", "cedict_1_0_ts_utf-8_mdbg.txt")
        except FileNotFoundError:
            try:
                with gzip.open("cedict_1_0_ts_utf-8_mdbg.txt.gz", 'rb') as g:
                    print("Found 'cedict_1_0_ts_utf-8_mdbg.txt.gz', extracting...")
                    with open("cedict_1_0_ts_utf-8_mdbg.txt", 'xb') as f:
                        shutil.copyfileobj(g, f)
            except FileNotFoundError:
                error_failed_to_read_dict()

try:
    parser.read_file("cedict_1_0_ts_utf-8_mdbg.txt")
except FileNotFoundError:
    error_failed_to_read_dict()

entries = parser.parse()

# Make a python dict out of the parsed CEDICT dictionary.
# Keys are the simplified/traditional word, and the values are a list of the corresponding `cedict.CedictEntry`'s.
dictionary = {}
for e in entries:
    dictionary[e.simplified] = dictionary.get(e.simplified, []) + [e]
    if(e.traditional != e.simplified):
        dictionary[e.traditional] = dictionary.get(e.traditional, []) + [e]


def find_all_words(s):
    """
    Finds all words in a given sentence which have an entry in the dictionary. Return format:
    ```
    # For input "ABCD"
    [
        [("ABC",...), ("AB",...), ("A",...)], # Words starting from the first characters
        [("BC",...), ("BC",...), ("B",...)],  # Words starting from the second character
        [("C",...)]                           # ...
    ]
    ```
    Each `...` is a `cedict.CedictEntry` corresponding to the word.
    """

    ret = []
    for i in range(len(s)):
        ret.append([])
        for j in range(len(s), i-1, -1):
            word = s[i:j]
            l = dictionary.get(word)
            if l is not None:
                ret[i].append((word, l))
            alt_word = "".join(map(lambda c: alternate_searches.get(c, c), word))
            if alt_word != word:
                al = dictionary.get(alt_word)
                if al is not None:
                    ret[i].append((alt_word, al))
    return ret


def main(stdscr):
    # curses.mousemask(1)

    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # stdscr.nodelay(True)

    stdscr.clear()

    sentence = ""
    words = [[]]
    cursor = 0
    update = True
    results = []
    selection = 0

    show_zhuyin = DEFAULT_READING_ZHUYIN

    def update_sentence(s):
        nonlocal sentence, words, update, cursor
        # sentence = s.replace("\n", " ").replace("\r", " ")
        sentence = "".join(s.split())
        words = find_all_words(sentence)
        update = True
        cursor = 0

    if len(argv) <= 1:
        update_sentence(pyperclip.paste())
    else:
        update_sentence(argv[1])

    while True:
        if update:
            update = False
            stdscr.clear()

            selection = 0
            results = []

            #### Render sentence and cursor ####

            stdscr.addstr(0, 0, sentence)
            if sentence != "":
                cursor_line = ""
                for i in range(cursor):
                    if unicodedata.east_asian_width(sentence[i]) in {"W", "F"}:
                        cursor_line += "　"
                    else:
                        cursor_line += " "
                if unicodedata.east_asian_width(sentence[cursor]) in {"W", "F"}:
                    cursor_line += "￣＼"
                else:
                    cursor_line += "‾\\"
                # stdscr.addstr(1, 0, ("　" * (cursor))+"￣＼")
                stdscr.addstr(1, 0, cursor_line)

            
            #### Render results ####

            line = 3

            if cursor < len(words):
                for w in words[cursor]:
                    defs = w[1]
                    for d in defs:
                        
                        results.append((line, d.simplified, d.traditional))

                        ## Parse pinyin for colours ##
                        colors = []
                        pinyins = d.pinyin.split(" ")
                        for p in pinyins:
                            if p[-1] in "12345":
                                colors.append(int(p[-1]))
                            else:
                                colors.append(5)

                        pos = 0
                        stdscr.addstr(line, pos, "　")
                        pos += 2

                        ## Word (Simplified) ##
                        for i in range(len(d.simplified)):
                            stdscr.addstr(line, pos, d.simplified[i], curses.color_pair(colors[i]))
                            pos += 1

                        stdscr.addstr(line, pos, "｜")
                        pos += 1

                        ## Word (Traditional) ##
                        for i in range(len(d.traditional)):
                            stdscr.addstr(line, pos, d.traditional[i], curses.color_pair(colors[i]))
                            pos += 1

                        stdscr.addstr(line, pos, "（")
                        pos += 1

                        ## Pinyin/Zhuyin ##
                        for i in range(len(pinyins)):
                            py = pinyins[i].replace(":", "") # Some CEDICT entrys contain ':' in the pinyin, the converter doesn't like that
                            if show_zhuyin:
                                try:
                                    z = transcriptions.pinyin_to_zhuyin(py)
                                except ValueError:
                                    z = py
                                stdscr.addstr(line, pos, z[:-1], curses.color_pair(colors[i]))
                                pos += len(z)

                                # Hacky shifting around of pos so we don't get overwritten characters or unwanted spaces
                                # Mixing fullwidth and halfwidth characters in curses is a pain...
                                if z[-1] in "ˉˇˋˊ˙":
                                    pos += 1
                                stdscr.addch(line, pos, z[-1], curses.color_pair(colors[i]))
                                pos += 2
                            else:
                                try:
                                    p = transcriptions.to_pinyin(py, accented=True)
                                except ValueError:
                                    p = py
                                stdscr.addstr(line, pos, p, curses.color_pair(colors[i]))
                                pos += len(py)
                        pos -= 1

                        stdscr.addstr(line, pos, "）：")
                        pos += 2

                        line += 1

                        for m in d.meanings:
                            stdscr.addstr(line, 4, m)
                            line += 1
                        line += 1

        for r in results:
            stdscr.addstr(r[0], 0, "　")
        if selection < len(results):
            stdscr.addstr(results[selection][0], 0, "＞")

        stdscr.refresh()
        key = curses.keyname(stdscr.getch()).decode('utf-8')

        print(f"Key pressed: '{key}'", file=logfile)

        if key == 'q' or key == '^[': # '^[' is ESC
            return
        elif key == ' ':
            update_sentence(pyperclip.paste())
        elif key == 'KEY_LEFT' or key == 'h':
            if cursor > 0:
                cursor -= 1
                update = True
        elif key == 'KEY_RIGHT' or key == 'l':
            if cursor < len(sentence) - 1:
                cursor += 1
                update = True
        elif key == 'KEY_UP' or key == 'k':
            if selection > 0:
                selection -= 1
                # update = True
        elif key == 'KEY_DOWN' or key == 'j':
            if selection < len(results) - 1:
                selection += 1
                # update = True
        elif key == 'KEY_END':
            cursor = len(sentence) - 1
            update = True
        elif key == 'KEY_HOME':
            cursor = 0
            update = True
        elif key == 'r':
            show_zhuyin = not show_zhuyin
            update = True
        elif key == 'a' or key == '^J': # '^J' is ENTER
            try:
                word = results[selection][2] if ADD_TRADITIONAL_CHARACTERS else results[selection][1]
                query = 'deck:"'+DECK+'" '+WORD_FIELD+':"'+word+'"'
                notes = anki('findNotes', query=query)
                # stdscr.addstr(30,0,str(notes))
                if len(notes) == 0:
                    field_names = anki('modelFieldNames', modelName=CARD_TYPE)
                    if WORD_FIELD in field_names:
                        fields = {f: "" for f in field_names}
                        fields[WORD_FIELD] = word
                        anki('addNote', note={
                            'deckName': DECK,
                            'modelName': CARD_TYPE,
                            'fields': fields,
                            'options': {}, 'tags': []})
                anki('guiBrowse', query=query)
            except Exception as e:
                y, _ = stdscr.getmaxyx()
                stdscr.addstr(y-1, 0, "Anki Error: " + str(e))
        else:
            if selection < len(results):
                word_simp = results[selection][1]
                word_trad = results[selection][2]
                if key == 'l' or key == 'KEY_F(1)':
                    webbrowser.open_new(f"https://dict.naver.com/linedict/zhendict/dict.html#/cnen/search?query={word_simp}")
                elif key == 'f' or key == 'KEY_F(2)':
                    webbrowser.open_new(f"https://forvo.com/word/{word_simp}/#zh")
                elif key == 'F' or key == 'KEY_F(14)':
                    webbrowser.open_new(f"https://forvo.com/word/{word_trad}/#zh")
                elif key == 'g' or key == 'KEY_F(3)':
                    webbrowser.open_new(f"https://resources.allsetlearning.com/chinese/grammar/{word_simp}")
                elif key == 'i' or key == 'KEY_F(4)':
                    webbrowser.open_new(f"https://www.iciba.com/word?w={word_simp}")
                elif key == 'm' or key == 'KEY_F(5)':
                    webbrowser.open_new(f"https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={word_simp}")
                elif key == 't' or key == 'KEY_F(6)':
                    webbrowser.open_new(f"https://www.moedict.tw/~{word_trad}")


curses.wrapper(main)
logfile.close()
