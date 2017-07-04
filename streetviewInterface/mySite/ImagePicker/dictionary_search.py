#
# Dictionaries from: http://www.gwicks.net/dictionaries.htm
# engmix.txt: ENGLISH - 84,000 words
# english3.txt: ENGLISH - 194,000 words
# usa.txt: USA ENGLISH - 61,000 words
# usa2.txt: USA ENGLISH - 77,000 words

# espanol.txt: SPANISH - 174,000 words

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

def english_or_spanish(ocr_text):
    words = ocr_text.split(" ")
    votes = []
    for word in words:
        best_match, best_distance, best_language = english_or_spanish_word(word)
        if best_language is not None:
            votes.append(best_language)
    spanish_votes = len([vote for vote in votes if vote == 'spanish'])
    english_votes = len([vote for vote in votes if vote == 'english'])
    if spanish_votes>english_votes:
        return 'spanish'
    elif spanish_votes<english_votes:
        return 'english'
    else:
        return None

# Output:
# best_language = spanish, english, or None
#
# best_language = None if MIN_LENGTH not satisfied
#                         edit distance too large
#                         spanish/english equally good
def english_or_spanish_word(ocr_text):
    MIN_LENGTH = 4
    MAX_DISTANCE_PERCENT = 0.3 # maximum distance cannot exceed MAX_DISTANCE_PERCENT * len(ocr_text)

    if len(ocr_text)<MIN_LENGTH:
        return None, None, None


    # test against spanish dictionary
    dictionary_spanish = load_words('dictionaries/espanol_utf8.txt')
    spanish_match, spanish_distance = score_language(ocr_text.lower(),dictionary_spanish)

    # test against english dictionary
    dictionary_english = load_words('dictionaries/engmix.txt')
    english_match, english_distance = score_language(ocr_text.lower(),dictionary_english)

    if spanish_match == None and english_match == None:
        best_match = None
        best_distance = None
        best_language = None
    elif spanish_match == None:
        best_match = english_match
        best_distance = english_distance
        best_language = 'english'
    else:
        if english_distance < spanish_distance:
            best_match = english_match
            best_distance = english_distance
            best_language = 'english'
        elif english_distance > spanish_distance:
            best_match = spanish_match
            best_distance = spanish_distance
            best_language = 'spanish'
        else:
            best_match = english_match + ', ' + spanish_match
            best_distance = english_distance
            best_language = None

    # maximum distance cannot exceed MAX_DISTANCE_PERCENT * len(ocr_text)
    if best_distance > MAX_DISTANCE_PERCENT * len(ocr_text):
        return None, None, None
    return best_match, best_distance, best_language

def score_language(ocr_text,dictionary):
    start_time = time.time()
    best_distance = 999999999999
    best_match = None
    for word in dictionary:
        d = editdistance.eval(ocr_text, word)
        if d<best_distance:
            best_distance = d
            best_match    = word
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    return best_match, best_distance
