from cedict_utils import cedict
from dragonmapper import transcriptions
from gtts import gTTS
import base64
import io
from anki import anki
from settings import *

DECK = "tmp"

parser = cedict.CedictParser()
parser.read_file("cedict_1_0_ts_utf-8_mdbg.txt")
entries = parser.parse()

dictionary = {}
for e in entries:
    e.pinyin = e.pinyin.replace("u:", "ü")
    dictionary[e.simplified] = dictionary.get(e.simplified, []) + [e]
    if(e.traditional != e.simplified):
        dictionary[e.traditional] = dictionary.get(e.traditional, []) + [e]


def add(word):
    unique_str = f"{word.simplified}|{word.traditional} ({word.pinyin})"
    query = f"deck:\"{DECK}\" {FIELD_UNIQUE}:\"{unique_str}\""
    filename = f"{word.simplified}_{word.traditional}_{''.join(word.pinyin.split())}.mp3"

    if len(anki('findNotes', query=query)) == 0:

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
        add_field(FIELD_PINYIN, colorize(transcriptions.to_pinyin(word.pinyin, accented=True).split(" ")))
        add_field(FIELD_ENGLISH, "<br>".join(word.meanings))

        if len(anki('getMediaFilesNames', pattern=filename)) == 0:
            tts_str = getattr(word, TTS_SRC_STRING)
            tts = gTTS(tts_str, lang=TTS_LANGUAGE)
            with io.BytesIO() as f:
                tts.write_to_fp(f)
                audio_b64 = base64.b64encode(f.getvalue()).decode('utf-8')
                anki('storeMediaFile', filename=filename, data=audio_b64)
        add_field(FIELD_SOUND, f"[sound:{filename}]")

        note = {'deckName': DECK, 'modelName': NOTE_TYPE, 'fields': fields, 'options': {}, 'tags': []}
        anki('addNote', note=note)
    # anki('guiBrowse', query=f"deck:{DECK} {FIELD_UNIQUE}:\"{unique_str}\"")


# ------------------------------------------------------------------------------------------------------

ids = anki('findNotes', query=f"deck:\">中文<\"")
infos = anki('notesInfo', notes=ids)
for n in infos:
    id = n['noteId']
    hanzi = n['fields']['Hanzi']['value']
    print(hanzi)
    entries = dictionary.get(hanzi)
    if entries is None:
        print("    No entries!")
    else:
        add(entries[0])
    # break
