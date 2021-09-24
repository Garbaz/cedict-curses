from cedict_utils import cedict
from sys import stderr
import os
import gzip
import zipfile
import shutil

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
