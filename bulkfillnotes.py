from dragonmapper import transcriptions
from anki import anki, fill_fields, unique_string
from sys import argv, stderr

try:
    from settings import *
except ModuleNotFoundError:
    print("Please start 'cedict-curses.py' once first so the settings file is set up.")
    exit(1)


if len(argv) > 1:
    query = argv[1]
else:
    print("Missing anki query...")
    exit(1)

notes = anki("findNotes", query=query)

input(f"Found {len(notes)} notes, continue?\nYes -> [ENTER]   |   No -> [CTRL+C]")

notesInfo = anki("notesInfo", notes=notes)

if True:  # `if True` to stop the autoformatter from moving the import to the top
    # Import takes a while, so only do it once it's clear we need it.
    from cedict import dictionary

for n in notesInfo:
    nonempty_fields = []
    empty_fields_exist = False
    for f in n['fields']:
        # print(f, n['fields'][f]['value'],len(n['fields'][f]['value']))
        if n['fields'][f]['value'] != "":
            nonempty_fields.append(f)
        else:
            empty_fields_exist = True

    if empty_fields_exist:  
        if FIELD_TRADITIONAL in nonempty_fields:
            entries = dictionary.get(n['fields'][FIELD_TRADITIONAL]['value'], [])
        elif FIELD_SIMPLIFIED in nonempty_fields:
            entries = dictionary.get(n['fields'][FIELD_SIMPLIFIED]['value'], [])
        else:
            print(f"Fields '{FIELD_TRADITIONAL}' and '{FIELD_SIMPLIFIED}' empty for note {n['noteId']}. Skipping!")
            continue

        word = None
        pinyin = ""
        if FIELD_PINYIN_NUMBERS in nonempty_fields:
            pinyin = n['fields'][FIELD_PINYIN_NUMBERS]['value']
        elif FIELD_PINYIN in nonempty_fields:
            pinyin = n['fields'][FIELD_PINYIN]['value']
        elif FIELD_ZHUYIN in nonempty_fields:
            pinyin = n['fields'][FIELD_ZHUYIN]['value']
        else:
            print(f"'{FIELD_PINYIN_NUMBERS}', '{FIELD_PINYIN}' and '{FIELD_ZHUYIN}' are empty for note {n['noteId']}. Assuming first entry!")
            word = entries[0]
        try:
            pinyin = transcriptions.to_pinyin(pinyin, accented=False)
        except ValueError:
            print(f"Bad pinyin/zhuyin in note {n['noteId']}. Skipping!")
            continue
        if word is None:
            syllables = pinyin.split()
            for i in range(len(syllables)):
                if syllables[i][-1] not in "12345":
                    syllables[i] += "5"
            clean_pinyin = ' '.join(syllables).lower()

            for e in entries:
                # print(e.pinyin.lower(), clean_pinyin)
                if e.pinyin.lower() == clean_pinyin:
                    word = e
                    break
        if word is None:
            print(f"Couldn't find cedict entry for character/reading combination of note {n['noteId']}. Will only fill pinyin/zhuyin fields!")
            fields = {FIELD_UNIQUE: unique_string(n['fields'][FIELD_SIMPLIFIED]['value'], n['fields'][FIELD_TRADITIONAL]['value'], pinyin),
                    FIELD_PINYIN_NUMBERS: pinyin,
                    FIELD_PINYIN: transcriptions.to_pinyin(pinyin, accented=True),
                    FIELD_ZHUYIN: transcriptions.to_zhuyin(pinyin),
                    }
        else:
            fields = fill_fields(word)

        # print(fields)

        for f in nonempty_fields:
            try:
                del fields[f]
            except KeyError:
                pass

        # print(fields)
        anki("updateNoteFields", note={'id': n['noteId'], 'fields': fields})

        # if n['noteId'] == 1475383622323:
        #     print(pinyin)
        #     print(fields)

        # exit(0)
