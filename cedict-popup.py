import curses
from sys import stderr
from cedict_utils.cedict import CedictParser
from dragonmapper import transcriptions
import curses
import pyperclip


parser = CedictParser()
try:
    parser.read_file("cedict_1_0_ts_utf-8_mdbg.txt")
except FileNotFoundError:
    print("Could not find dictionary file 'cedict_1_0_ts_utf-8_mdbg.txt'! Please download CC-CEDICT from",file=stderr)
    print("https://www.mdbg.net/chinese/dictionary?page=cedict",file=stderr)
    print("and extract it in this folder.",file=stderr)
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

    def read_clipboard():
        nonlocal sentence, words, update
        sentence = pyperclip.paste()
        words = find_all_words(sentence)
        update = True
    
    read_clipboard()

    while True:
        if update:
            update = False
            stdscr.clear()

            stdscr.addstr(0, 0, sentence)
            stdscr.addstr(1, 0, ("　" * (cursor))+"￣＼")

            line = 3
            for w in words[cursor]:
                defs = w[1]
                for d in defs:
                    colors = []
                    pinyins = d.pinyin.split(" ")
                    for p in pinyins:
                        if p[-1] in "12345":
                            colors.append(int(p[-1]))
                        else:
                            colors.append(5)

                    pos = 0

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
                    for i in range(len(pinyins)):
                        try:
                            z = transcriptions.pinyin_to_zhuyin(pinyins[i])
                        except ValueError:
                            z = pinyins[i]
                        stdscr.addstr(line, pos, z, curses.color_pair(colors[i]))
                        pos += len(z)
                        stdscr.addstr(line, pos, " ˉˊˇˋ˙"[colors[i]], curses.color_pair(colors[i]))
                        pos += 1

                    stdscr.addstr(line, pos, "）：")
                    pos += 2
                    line += 1

                    for m in d.meanings:
                        stdscr.addstr(line, 4, m)
                        line += 1
                    line += 1

        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            return
        elif key == ord(' '):
            read_clipboard()
        elif key == curses.KEY_LEFT:
            if cursor > 0:
                cursor -= 1
                update = True
        elif key == curses.KEY_RIGHT:
            if cursor < len(sentence) - 1:
                cursor += 1
                update = True
        elif key == curses.KEY_UP:
            cursor = 0
            update = True
        elif key == curses.KEY_DOWN:
            cursor = len(sentence) - 1
            update = True


curses.wrapper(main)
