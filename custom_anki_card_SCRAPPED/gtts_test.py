from gtts import gTTS

lang = 'zh-tw'

test_hanzi = "得"
test_zhuyin = "ㄉㄟˇ"
test_pinyin = "děi"

gTTS(test_hanzi,  lang=lang).save("test_hanzi.mp3")
gTTS(test_zhuyin, lang=lang).save("test_zhuyin.mp3")
gTTS(test_pinyin, lang=lang).save("test_pinyin.mp3")