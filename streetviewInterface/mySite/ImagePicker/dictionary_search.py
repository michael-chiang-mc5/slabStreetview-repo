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
      # print(" ", len(wordlist), "words loaded.")
       return wordlist




#count_space = 0
#for word in wordlist:
#    for letter in word:
#        if letter not in 'abcdefghijklmnopqrstuvwxyz':
#            print(word)
#            print(letter)
#            count_space = count_space + 1




def filter_words(text_list, word_min_length):
    out = []
    for text in text_list:
        omit = False
        if len(text)<word_min_length:
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
def english_or_spanish(words, word_min_length=4,match_threshold=1,word_count_threshold=1):
    words = re.split('&| |,|-,|_|\n|\.',words) # split string
    words = filter_words(words, word_min_length) # throw out words with numbers,

    dictionary_spanish = load_words('dictionaries/espanol_utf8.txt')
    dictionary_english = load_words('dictionaries/engmix.txt')

    count_spanish = 0
    count_english = 0

    for word in words:
        # check if word is spanish
        if match_threshold == 0:
            word_is_spanish = score_language_fast(word,dictionary_spanish)
        else:
            spanish_match, spanish_distance = score_language(word,dictionary_spanish)
            if spanish_distance<=match_threshold:
                word_is_spanish = True
            else:
                word_is_spanish = False

        # check if word is english
        if match_threshold == 0:
            word_is_english = score_language_fast(word,dictionary_english)
        else:
            english_match, english_distance = score_language(word,dictionary_english)
            if english_distance<=match_threshold:
                word_is_english = True
            else:
                word_is_english = False
        #print(word_is_english)
        #print(word)
        #print(word.lower() == 'grill')
        if word_is_spanish and not word_is_english:
            count_spanish += 1
        if word_is_english and not word_is_spanish:
            count_english += 1

    return {'english':count_english>=word_count_threshold, \
            'spanish':count_spanish>=word_count_threshold, \
            }

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
    #print(elapsed_time)
    return best_match, best_distance

def score_language_fast(ocr_text,dictionary):
    for word in dictionary:
        if ocr_text.lower() == word:
            return True
    return False
