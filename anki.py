import json
from typing import Type
import urllib.request
from dragonmapper import transcriptions

try:
    from settings import *
except ModuleNotFoundError:
    print("Please start 'cedict-curses.py' once first so the settings file is set up.")
    exit(1)


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def anki(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def unique_string(word):
    pinyin_numbers = word.pinyin.replace(" ", "")
    return  f"{word.simplified}[{word.traditional}] {pinyin_numbers}"


def fill_fields(word):
    fields = {}

    def add_field(name, value):
        nonlocal fields
        if name != "":
            fields[name] = value

    colors = [(p[-1] if p[-1] in "12345" else "5") for p in word.pinyin.split(" ")]

    def colorize(array):
        return "".join([f"<span class=\"tone{c}\">{s}</span>" for c, s in zip(colors, array)])

    add_field(FIELD_UNIQUE, unique_string(word))
    add_field(FIELD_SIMPLIFIED, word.simplified)
    add_field(FIELD_SIMPLIFIED_COLOR, colorize(word.simplified))
    add_field(FIELD_TRADITIONAL, word.traditional)
    add_field(FIELD_TRADITIONAL_COLOR, colorize(word.traditional))
    add_field(FIELD_ZHUYIN, colorize(transcriptions.to_zhuyin(word.pinyin).split(" ")))
    add_field(FIELD_PINYIN, transcriptions.to_pinyin(word.pinyin))
    add_field(FIELD_PINYIN_COLOR, colorize(transcriptions.to_pinyin(word.pinyin, accented=True).split(" ")))
    add_field(FIELD_PINYIN_NUMBERS, word.pinyin.replace(" ", ""))
    add_field(FIELD_ENGLISH, "<br>".join(word.meanings))
    
    return fields



def add_note(word):
    # pinyin_numbers = word.pinyin.replace(" ", "")
    # pinyin_accented = transcriptions.to_pinyin(word.pinyin, accented=True)
    # zhuyin = transcriptions.to_zhuyin(word.pinyin)

    unique_str = unique_string(word)
    query = f"deck:\"{DECK}\" {FIELD_UNIQUE}:\"{unique_str}\""
    # filename = f"{word.simplified}_{word.traditional}_{''.join(word.pinyin.split())}.mp3"

    note_ids = anki('findNotes', query=query)

    if len(note_ids) == 0:

        # if len(anki('getMediaFilesNames', pattern=filename)) == 0:
        #     tts_str = getattr(word, TTS_SRC_STRING)
        #     tts = gTTS(tts_str, lang=TTS_LANGUAGE)
        #     with io.BytesIO() as f:
        #         tts.write_to_fp(f)
        #         audio_b64 = base64.b64encode(f.getvalue()).decode('utf-8')
        #         anki('storeMediaFile', filename=filename, data=audio_b64)
        # add_field(FIELD_SOUND, f"[sound:{filename}]")

        note = {'deckName': DECK, 'modelName': NOTE_TYPE, 'fields': fill_fields(word), 'options': {'duplicateScope': "deck"}, 'tags': []}
        note_ids = [anki('addNote', note=note)]
    anki('addTags', notes=note_ids, tags="marked")
    anki('guiBrowse', query=f"deck:{DECK} {FIELD_UNIQUE}:\"{unique_str}\"")

