import requests
from functools import lru_cache
import re
import emoji
import os
import string
import nltk
import random
import numpy as np
from nltk.stem import WordNetLemmatizer
from emojisearch import search
from random import randint
from .emojifi_searcher import valid_word_to_emoji_freqs

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
STOPWORD_PATH = 'stopwords.txt'
PRE_URL = "https://emojifinder.com/ajax.php?action=search&query="
POST_URL = "&fbclid=IwAR2ISsQB4n2lkpYeyfKgtGGa2Yhj-xQS_0uu8WJ3Bqa7wZNQl6hj_a6CF5w"
SUBSTRING_TO_EMOJI = {
    'ea': '00C6',
    'ae': '00C6',
    'ab': '1F18E',
    'cl': '1F191',
    'cool': '1F192',
    'ok': '1F197',
    'ng': '1F196',
}
LETTER_TO_EMOJI = {
    'a': '1F170',
    'b': '1F171',
    'c': '1F172',
    'm': '24C2',
    'o': '1F17E',
    'p': '1F17F',
    'x': '274E',
}

VOWELS = ['a', 'e', 'i', 'o', 'u']


# Initialize the lemmer at compile time
LEM_FUNC = WordNetLemmatizer().lemmatize
LEM_FUNC('a', pos='v') # Forces the lemmatizer to load at start


@lru_cache(maxsize=1)
def load_stopwords():
    """ Reads the stopwords file and loads it into a set """
    with open(os.path.join(BASE_PATH, STOPWORD_PATH)) as f:
        return set(f.read().splitlines())


def next_word(text):
    """ Generator yielding the next word in a text """
    for word in text.split():
        yield word


def is_valid_word(word, stopwords):
    """ Returns whether a word is valid:
        (non-stop word and no character other than a-zA-Z)"""
    return word in stopwords and word.isalpha()


def emojifi_text(text):
    """ Emojifies text by inserting emojis around valid words """
    random.seed(5)
    np.random.seed(5)
    result = []
    stopwords = load_stopwords()

    for word in next_word(text):
        result.append(_emojifi_word(word, stopwords))

    return ' '.join(result)


def clappifi_text(text):
    """ Emojifies text by inserting claps around every word """
    if text:
        clap = emoji.emojize(' :clap: ', use_aliases=True)
        return clap.join(text.split()) + clap
    return ""


def radomized_case(text):
    return text.upper() if random.randint(0, 1) else text.lower()


def spongebobifi_text(text):
    random.seed(5)
    return ''.join(radomized_case(char) for char in text)


def memeifi_text(text):
    """ Emojifies text by inserting emojis around valid words """
    result = []

    for word in next_word(text):
        result.append(_memeifi_word(word))

    return ' '.join(result)


def _memeifi_word(word):
    wordy = word
    result = []
    for ss in SUBSTRING_TO_EMOJI:
        wordy = wordy.replace(ss, _plaintext_hex_to_unicode(SUBSTRING_TO_EMOJI[ss]))

    for c in wordy:
        if c in LETTER_TO_EMOJI:
            result.append(_plaintext_hex_to_unicode(LETTER_TO_EMOJI[c]))
        else:
            result.append(c)
    return ''.join(result)


def _has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def clean_word(word):
    """ Removes punctuation and lemmatizes the word if applicable """
    try:
        clean = LEM_FUNC(word, pos='v')
    except Exception:
        clean = word

    return clean.translate(str.maketrans('', '', string.punctuation))


def _emojifi_word(word, stopwords):
    """ Returns a word concat with an emoji if the word requires one """
    wordy = word
    emojis = ''

    if word not in stopwords and not _has_numbers(word):
        cleaned_word = clean_word(word)
        freqs = valid_word_to_emoji_freqs(cleaned_word)
        top_n = freqs[0:emojis_collected()]

        emojis = ''.join([emoji.emojize(x) * emojis_repeated() for x in top_n])

    """ Emojifies text by replacing some word's first letters with regional indicator b"""
    if word and len(word) > 0:
        wordy = beeify(wordy)
    return wordy + ' ' + emojis + ' '


def beeify(word):
    """ Randomly replaces a word's first letter with the B emoji if applicable """
    def is_beeifyable(word):
        """ Determines if a word can be beeifyable """
        return len(word) > 1 and word[0].lower() not in VOWELS

    def can_beeify():
        """ Determines if the random chance to beeify has occured """
        return randint(0, 15) == 0

    @lru_cache(maxsize=1)
    def b_emoji():
        """ Returns the B emoji """
        return _plaintext_hex_to_unicode(LETTER_TO_EMOJI['b'])

    def beeify_valid_word(word):
        """ Beeify's a word, assuming is_beeifyable() and can_beeify() were true """
        return ''.join([b_emoji()] + list(word[1::]))

    if is_beeifyable(word) and can_beeify():
        return beeify_valid_word(word)

    return word

def emojis_collected():
    return 1 + np.random.poisson(.30)


def emojis_repeated():
    return 1 + np.random.poisson(.30)


def _plaintext_hex_to_unicode(code):
    return chr(int(code, 16))
