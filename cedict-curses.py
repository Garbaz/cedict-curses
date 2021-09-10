import curses
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

try:
    from settings import *
except ModuleNotFoundError:
    shutil.copy(".default_settings.py","settings.py")
    print("Please open the file \'settings.py\' in a text editor and set the settings.",file=stderr)
    print("Afterwards, start the program again.")
    input("\n(Press ENTER to exit...)")
    exit(1)

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


# Try to load dictionary file.
# If the file isn't found, try to find other forms of the file and extract/rename.
try:
    parser = cedict.CedictParser(file_path="cedict_1_0_ts_utf-8_mdbg.txt")
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
    parser = cedict.CedictParser(file_path="cedict_1_0_ts_utf-8_mdbg.txt")
except FileNotFoundError:
    error_failed_to_read_dict()

parsed = parser.parse()

# Make a python dict out of the parsed CEDICT dictionary.
# Keys are the simplified/traditional word, and the values are a list of the corresponding `cedict.CedictEntry`'s.
dictionary = {}
for e in parsed:
    e.pinyin.replace("u:", "ü")
    dictionary[e.simplified] = dictionary.get(e.simplified, []) + [e]
    if(e.traditional != e.simplified):
        dictionary[e.traditional] = dictionary.get(e.traditional, []) + [e]


def find_all_words(s):
    """
    Finds all words in a given sentence which have an entry in the dictionary. Return format:
    ```
    # For input "ABCD"
    [
        [("ABC",...), ("AB",...), ("A",...)], # Words starting from the first character
        [("BC",...), ("BC",...), ("B",...)],  # Words starting from the second character
        [("C",...)],                          # ...
        [("D",...)]
    ]
    ```
    Each `...` is a `cedict.CedictEntry` corresponding to the word.
    """

    ret = []
    for i in range(len(s)):
        ret.append([])
        for j in range(len(s), i-1, -1):
            word = s[i:j]
            entries = dictionary.get(word)
            if entries is not None:
                ret[i].append((word, entries))
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

            #### Render sentence ####

            # There might be a cleaner way, but this way I ensure the sentence
            # is rendered on every second line, without having to manually deal
            # with full-width and half-width characters myself.
            sent_y, sent_x = 0, 0
            for c in sentence:
                stdscr.addstr(sent_y, sent_x, c)
                y, x = stdscr.getyx()
                sent_x = x
                if y != sent_y:
                    sent_y += 2

            #### Render cursor ####
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
                # stdscr.addstr(1, 0, cursor_line)

                # Same code as with sentence, just offset by one line
                curs_y, curs_x = 1, 0
                for c in cursor_line:
                    stdscr.addstr(curs_y, curs_x, c)
                    y, x = stdscr.getyx()
                    curs_x = x
                    if y != curs_y:
                        curs_y += 2

            #### Render results ####

            line = sent_y + 2

            max_y, max_x = stdscr.getmaxyx()

            def addstr_at_line(x_offset, text, *args, **vargs):
                nonlocal line
                if line < max_y - 1:
                    if x_offset == -1:
                        _, x_offset = stdscr.getyx()
                    stdscr.addstr(line, x_offset, text, *args, **vargs)
                else:
                    stdscr.addstr(max_y - 1, 0, "(( Too many results! Make window bigger ))")

            def addstr_at_line_seq(text, *args, **vargs):
                addstr_at_line(-1, text, *args, **vargs)
            # def addch_at_line()

            if cursor < len(words):
                for w in words[cursor]:
                    entries = w[1]
                    for e in entries:
                        results.append((line, e))

                        ## Parse pinyin for colours ##
                        colors = []
                        pinyins = e.pinyin.split(" ")
                        for p in pinyins:
                            if p[-1] in "12345":
                                colors.append(int(p[-1]))
                            else:
                                colors.append(5)

                        addstr_at_line(0, "　")

                        ## Word (Simplified) ##
                        for i in range(len(e.simplified)):
                            addstr_at_line_seq(e.simplified[i], curses.color_pair(colors[i]))
                        addstr_at_line_seq("｜")

                        ## Word (Traditional) ##
                        for i in range(len(e.traditional)):
                            addstr_at_line_seq(e.traditional[i], curses.color_pair(colors[i]))

                        ## Pinyin/Zhuyin ##
                        addstr_at_line_seq("（")
                        for i in range(len(pinyins)):
                            pinyin = pinyins[i]
                            try:
                                if show_zhuyin:
                                    reading = transcriptions.to_zhuyin(pinyin)
                                else:
                                    reading = transcriptions.to_pinyin(pinyin, accented=True)
                            except ValueError:
                                reading = pinyin
                            addstr_at_line_seq(reading, curses.color_pair(colors[i]))
                        addstr_at_line_seq("）：")

                        line += 1

                        ## Meanings ##
                        for m in e.meanings:
                            addstr_at_line(4, m)
                            line += 1
                        line += 1

        for r in results:
            if r[0] < max_y - 1:
                stdscr.addstr(r[0], 0, "　")
        if selection < len(results):
            if results[selection][0] < max_y - 1:
                stdscr.addstr(results[selection][0], 0, "＞")

        stdscr.refresh()
        key = curses.keyname(stdscr.getch()).decode('utf-8')

        # print(f"Key pressed: '{key}'", file=logfile)

        def move_cursor_clamp(new_cursor):
            nonlocal cursor
            old_cursor = cursor
            cursor = new_cursor
            if cursor < 0:
                cursor = 0
            elif cursor >= len(sentence):
                cursor = len(sentence) - 1
            return old_cursor != cursor

        if key == 'q' or key == '^[':  # '^[' is ESC
            return
        elif key == ' ' or key == 'M-c':  # 'M-c' is for wide space (not accurate, but works)
            update_sentence(pyperclip.paste())
        elif key == 'KEY_LEFT' or key == 'h':
            update |= move_cursor_clamp(cursor-1)
        elif key == 'KEY_RIGHT' or key == 'l':
            update |= move_cursor_clamp(cursor+1)
        elif key == 'KEY_END':
            update |= move_cursor_clamp(len(sentence) - 1)
        elif key == 'KEY_HOME':
            update |= move_cursor_clamp(0)
        elif key == 'KEY_PPAGE':
            update |= move_cursor_clamp(cursor-10)
        elif key == 'KEY_NPAGE':
            update |= move_cursor_clamp(cursor+10)
        elif key == 'KEY_UP' or key == 'k':
            if selection > 0:
                selection -= 1
        elif key == 'KEY_DOWN' or key == 'j':
            if selection < len(results) - 1:
                selection += 1
        elif key == 'r':
            show_zhuyin = not show_zhuyin
            update = True
        elif key == 'a' or key == '^J':  # '^J' is ENTER
            try:
                word : cedict.CedictEntry = results[selection][1]
                pinyin_numbers = word.pinyin.replace(" ", "")
                pinyin_accented = transcriptions.to_pinyin(word.pinyin,accented=True)
                zhuyin = transcriptions.to_zhuyin(word.pinyin)

                unique_str = f"{word.simplified}[{word.traditional}] {pinyin_numbers}"
                query = f"deck:\"{DECK}\" {FIELD_UNIQUE}:\"{unique_str}\""
                # filename = f"{word.simplified}_{word.traditional}_{''.join(word.pinyin.split())}.mp3"
                
                note_ids = anki('findNotes', query=query)

                if len(note_ids) == 0:

                    fields = {}

                    def add_field(name, value):
                        nonlocal fields
                        if name != "":
                            fields[name] = value

                    colors = [(p[-1] if p[-1] in "12345" else "5") for p in word.pinyin.split(" ")]

                    def colorize(array):
                        return "".join([f"<span class=\"tone{c}\">{s}</span>" for c, s in zip(colors, array)])

                    add_field(FIELD_UNIQUE, unique_str)
                    add_field(FIELD_SIMPLIFIED, word.simplified)
                    add_field(FIELD_SIMPLIFIED_COLOR, colorize(word.simplified))
                    add_field(FIELD_TRADITIONAL, word.traditional)
                    add_field(FIELD_TRADITIONAL_COLOR, colorize(word.traditional))
                    add_field(FIELD_ZHUYIN, colorize(transcriptions.to_zhuyin(word.pinyin).split(" ")))
                    add_field(FIELD_PINYIN, transcriptions.to_pinyin(word.pinyin))
                    add_field(FIELD_PINYIN_COLOR, colorize(transcriptions.to_pinyin(word.pinyin, accented=True).split(" ")))
                    add_field(FIELD_PINYIN_NUMBERS, word.pinyin.replace(" ",""))
                    add_field(FIELD_ENGLISH, "<br>".join(word.meanings))

                    # if len(anki('getMediaFilesNames', pattern=filename)) == 0:
                    #     tts_str = getattr(word, TTS_SRC_STRING)
                    #     tts = gTTS(tts_str, lang=TTS_LANGUAGE)
                    #     with io.BytesIO() as f:
                    #         tts.write_to_fp(f)
                    #         audio_b64 = base64.b64encode(f.getvalue()).decode('utf-8')
                    #         anki('storeMediaFile', filename=filename, data=audio_b64)
                    # add_field(FIELD_SOUND, f"[sound:{filename}]")

                    note = {'deckName': DECK, 'modelName': NOTE_TYPE, 'fields': fields, 'options': {'duplicateScope': "deck"}, 'tags': []}
                    note_ids = [anki('addNote', note=note)]
                anki('addTags', notes=note_ids, tags="marked")
                anki('guiBrowse', query=f"deck:{DECK} {FIELD_UNIQUE}:\"{unique_str}\"")

            except Exception as e:
                stdscr.addstr(max_y-1, 0, f"(( Anki Error: {str(e)} ))")
        else:
            if selection < len(results):
                word_simp = results[selection][1].simplified
                word_trad = results[selection][1].traditional
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
