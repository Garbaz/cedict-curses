import curses
from sys import argv
from dragonmapper import transcriptions
import pyperclip
import webbrowser
import unicodedata
import shutil

try:
    from settings import *
except ModuleNotFoundError:
    shutil.copy(".default_settings.py", "settings.py")
    print("Please open the file 'settings.py' in a text editor and set the settings.")
    print("Afterwards, start the program again.")
    input("\n(Press ENTER to exit...)")
    exit(1)

from anki import add_note
from cedict import find_all_words

logfile = open("cedict-curses.log", "w")


def main(stdscr):
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
    
    # curses.mousemask(curses.BUTTON3_PRESSED)
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # stdscr.nodelay(True)

    stdscr.clear()


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
                    stdscr.addstr(
                        max_y - 1, 0, "(( Too many results! Make window bigger ))"
                    )

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
                            addstr_at_line_seq(
                                e.simplified[i], curses.color_pair(colors[i])
                            )
                        addstr_at_line_seq("｜")

                        ## Word (Traditional) ##
                        for i in range(len(e.traditional)):
                            addstr_at_line_seq(
                                e.traditional[i], curses.color_pair(colors[i])
                            )

                        ## Pinyin/Zhuyin ##
                        addstr_at_line_seq("（")
                        for i in range(len(pinyins)):
                            pinyin = pinyins[i]
                            try:
                                if show_zhuyin:
                                    reading = transcriptions.to_zhuyin(pinyin)
                                else:
                                    reading = transcriptions.to_pinyin(
                                        pinyin, accented=True
                                    )
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
        key = curses.keyname(stdscr.getch()).decode("utf-8")

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

        if key == "q" or key == "^[":  # '^[' is ESC
            return
        elif (
            key == " " or key == "M-c"
        ):  # 'M-c' is for wide space (not accurate, but works)
            update_sentence(pyperclip.paste())
        elif key == "KEY_LEFT" or key == "h":
            update |= move_cursor_clamp(cursor - 1)
        elif key == "KEY_RIGHT" or key == "l":
            update |= move_cursor_clamp(cursor + 1)
        elif key == "KEY_END":
            update |= move_cursor_clamp(len(sentence) - 1)
        elif key == "KEY_HOME":
            update |= move_cursor_clamp(0)
        elif key == "KEY_PPAGE":
            update |= move_cursor_clamp(cursor - 10)
        elif key == "KEY_NPAGE":
            update |= move_cursor_clamp(cursor + 10)
        elif key == "KEY_UP" or key == "k":
            if selection > 0:
                selection -= 1
        elif key == "KEY_DOWN" or key == "j":
            if selection < len(results) - 1:
                selection += 1
        elif key == "r":
            show_zhuyin = not show_zhuyin
            update = True
        elif key == "a" or key == "^J":  # '^J' is ENTER
            try:
                if add_note(results[selection][1]):
                    stdscr.addstr(max_y - 1, 0, f"(( Anki: Added new note for \"{results[selection][1].simplified}|{results[selection][1].traditional}\". ))")
                else:
                    stdscr.addstr(max_y - 1, 0, f"(( Anki: Found & marked note for \"{results[selection][1].simplified}|{results[selection][1].traditional}\". ))")    
            except Exception as e:
                stdscr.addstr(max_y - 1, 0, f"(( Anki ERROR: {str(e)} ))")
        else:
            if selection < len(results):
                word_simp = results[selection][1].simplified
                word_trad = results[selection][1].traditional
                if key == "l" or key == "KEY_F(1)":
                    webbrowser.open_new(
                        f"https://dict.naver.com/linedict/zhendict/dict.html#/cnen/search?query={word_simp}"
                    )
                elif key == "f" or key == "KEY_F(2)":
                    webbrowser.open_new(f"https://forvo.com/word/{word_simp}/#zh")
                elif key == "F" or key == "KEY_F(14)":
                    webbrowser.open_new(f"https://forvo.com/word/{word_trad}/#zh")
                elif key == "g" or key == "KEY_F(3)":
                    webbrowser.open_new(
                        f"https://resources.allsetlearning.com/chinese/grammar/{word_simp}"
                    )
                elif key == "i" or key == "KEY_F(4)":
                    webbrowser.open_new(f"https://www.iciba.com/word?w={word_simp}")
                elif key == "m" or key == "KEY_F(5)":
                    webbrowser.open_new(
                        f"https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={word_simp}"
                    )
                elif key == "t" or key == "KEY_F(6)":
                    webbrowser.open_new(f"https://www.moedict.tw/~{word_trad}")


curses.wrapper(main)
logfile.close()
