from utils import (
	write_json_cache, 
	read_json_cache,
	valid_words)

from assets.dictionaries import SimpleDict

import os
from string import ascii_lowercase as alphabet




ANAGRAMS_FILE = './assets/anagrams.json'
FIVE_LETTER_WORDS_FILE = './assets/all_five_letter_words.txt'
BEST_WEIGHTS_FILE = './assets/wordle_weights.json'
WORDLE_ANSWER_WORDS = './assets/wordle_possible_answer_words.txt'

wordle_answer_dictionary = SimpleDict(WORDLE_ANSWER_WORDS)
wordle_accepted_dictionary = SimpleDict(FIVE_LETTER_WORDS_FILE)

default_known_anagrams = {}
all_five_letter_words = set(wordle_accepted_dictionary.words_list)

def build_known_anagrams(alphabet=alphabet, dictionary=wordle_accepted_dictionary, known_anagrams=default_known_anagrams):
	if os.path.exists(ANAGRAMS_FILE):
		try:
			return read_json_cache(ANAGRAMS_FILE)
		except:
			valid_words(alphabet, dictionary, known_anagrams)
			return known_anagrams
	else:
		valid_words(alphabet, dictionary, known_anagrams)
		return known_anagrams


def get_all_five_letter_words():
	global all_five_letter_words
	return all_five_letter_words.copy()

def write_known_anagrams(anagrams):
	write_json_cache(anagrams, ANAGRAMS_FILE)