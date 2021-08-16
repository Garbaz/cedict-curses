import curses
from sys import stderr, argv
from cedict_utils.cedict import CedictParser
from dragonmapper import transcriptions
import curses
import pyperclip


parser = CedictParser()

try:
    parser.read_file("cedict_1_0_ts_utf-8_mdbg.txt")
except FileNotFoundError:
    print("Could not find dictionary file 'cedict_1_0_ts_utf-8_mdbg.txt'! Please download CC-CEDICT from", file=stderr)
    print("https://www.mdbg.net/chinese/dictionary?page=cedict", file=stderr)
    print("and extract it in this folder.", file=stderr)
    exit(1)

entries = parser.parse()

dictionary = {}
for e in entries:
    dictionary[e.simplified] = dictionary.get(e.simplified, []) + [e]
    if(e.traditional != e.simplified):
        dictionary[e.traditional] = dictionary.get(e.traditional, []) + [e]


def find_all_words(s):
    ret = []
    for i in range(len(s)):
        ret.append([])
        for j in range(len(s), i-1, -1):
            word = s[i:j]
            l = dictionary.get(word)
            if l is not None:
                ret[i].append((word, l))
    return ret

# for ws in find_all_words(sentence).values():
#     for w in ws:
#         print(w[0],w[1])
# exit()


def main(stdscr: curses.window):
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

    sentence = " "
    words = [[]]
    cursor = 0
    update = True
    results = []
    result_selection = 0

    show_zhuyin = True

    def update_sentence(s):
        nonlocal sentence, words, update, cursor
        sentence = s
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

            result_selection = 0
            results = []

            stdscr.addstr(0, 0, sentence)
            stdscr.addstr(1, 0, ("　" * (cursor))+"￣＼")

            line = 3

            if cursor < len(words):
                for w in words[cursor]:
                    defs = w[1]
                    for d in defs:

                        results.append((line, d.simplified))

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

                        for i in range(len(d.simplified)):
                            stdscr.addstr(line, pos, d.simplified[i], curses.color_pair(colors[i]))
                            pos += 1

                        stdscr.addstr(line, pos, "｜")
                        pos += 1
                        for i in range(len(d.traditional)):
                            stdscr.addstr(line, pos, d.traditional[i], curses.color_pair(colors[i]))
                            pos += 1

                        stdscr.addstr(line, pos, "（")
                        pos += 1

                        # for i in range(len(pinyins)):
                        #     stdscr.addstr(line, pos, pinyins[i], curses.color_pair(colors[i]))
                        #     pos += len(pinyins[i])

                        # stdscr.addstr(line, pos, "｜")
                        # pos += 1

                        for i in range(len(pinyins)):
                            
                            if show_zhuyin:
                                try:
                                    z = transcriptions.pinyin_to_zhuyin(pinyins[i])
                                except ValueError:
                                    z = pinyins[i]
                                stdscr.addstr(line, pos, z[:-1], curses.color_pair(colors[i]))
                                pos += len(z)
                                stdscr.addch(line, pos, z[-1], curses.color_pair(colors[i]))
                                pos += 2
                            else:
                                try:
                                    p = transcriptions.ipa_to_pinyin(transcriptions.pinyin_to_ipa(pinyins[i]))
                                except ValueError:
                                    p = pinyins[i]
                                stdscr.addstr(line, pos, p, curses.color_pair(colors[i]))
                                pos += len(pinyins[i])
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

        if result_selection < len(results):
            stdscr.addstr(results[result_selection][0], 0, "＞")
            # stdscr.addstr(30,0,str(result_selection))
        # for i in range(len(results)):
        #     stdscr.addstr(30+i,0,str(results[i]))

        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            return
        elif key == ord(' '):
            update_sentence(pyperclip.paste())
        elif key == curses.KEY_LEFT:
            if cursor > 0:
                cursor -= 1
                update = True
        elif key == curses.KEY_RIGHT:
            if cursor < len(sentence) - 1:
                cursor += 1
                update = True
        elif key == curses.KEY_UP:
            if result_selection > 0:
                result_selection -= 1
                # update = True
        elif key == curses.KEY_DOWN:
            if result_selection < len(results) - 1:
                result_selection += 1
                # update = True
        elif key == ord("r"):
            show_zhuyin = not show_zhuyin
            update = True


curses.wrapper(main)
