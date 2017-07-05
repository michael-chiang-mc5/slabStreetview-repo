#
# Dictionaries from: http://www.gwicks.net/dictionaries.htm
# engmix.txt: ENGLISH - 84,000 words
# english3.txt: ENGLISH - 194,000 words
# usa.txt: USA ENGLISH - 61,000 words
# usa2.txt: USA ENGLISH - 77,000 words

# espanol.txt: SPANISH - 174,000 words
import re
import editdistance
import time

def load_words(WORDLIST_FILENAME):
       #print("Loading word list from file...")
       wordlist = list()
       # 'with' can automate finish 'open' and 'close' file
       with open(WORDLIST_FILENAME, encoding = "ISO-8859-1") as f:
            # fetch one line each time, include '\n'
            for line in f:
                # strip '\n', then append it to wordlist
                wordlist.append(line.rstrip('\n'))
       print(" ", len(wordlist), "words loaded.")
       return wordlist




#count_space = 0
#for word in wordlist:
#    for letter in word:
#        if letter not in 'abcdefghijklmnopqrstuvwxyz':
#            print(word)
#            print(letter)
#            count_space = count_space + 1




def filter_words(text_list):
    MIN_LENGTH = 4
    out = []
    for text in text_list:
        omit = False
        if len(text)<MIN_LENGTH:
            omit = True
        for letter in text:
            if letter in '1234567890!@#$%^&*()':
                omit = True
        text = text.replace("'","")
        if not omit:
            out.append(text)
    return out

# input:
#     words: string
def english_or_spanish(words):
    words = re.split('&| |,|-',words)
    words = filter_words(words)

    dictionary_spanish = load_words('dictionaries/espanol_utf8.txt')
    dictionary_english = load_words('dictionaries/engmix.txt')

    combined_spanish_distance = 0
    combined_english_distance = 0
    combined_spanish = "spanish = "
    combined_english = "english = "

    for word in words:
        spanish_match, spanish_distance = score_language(word,dictionary_spanish)
        english_match, english_distance = score_language(word,dictionary_english)

        combined_spanish_distance+=spanish_distance
        combined_english_distance+=english_distance
        combined_spanish+=spanish_match + '('+word+')* '
        combined_english+=english_match + '('+word+')* '

    if combined_spanish_distance<combined_english_distance:
        best_language = 'spanish'
    elif combined_spanish_distance>combined_english_distance:
        best_language = 'english'
    else:
        best_language = 'equal english/spanish score'

    notes = combined_spanish + " ////////////// " + combined_english
    return best_language,notes

def score_language(ocr_text,dictionary):
    start_time = time.time()
    best_distance = 999999999999
    best_match = None
    for word in dictionary:
        d = editdistance.eval(ocr_text.lower(), word)
        if d<best_distance:
            best_distance = d
            best_match    = word
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    return best_match, best_distance
