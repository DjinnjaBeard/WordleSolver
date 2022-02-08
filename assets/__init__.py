from utils import (
	write_json_cache, 
	read_json_cache,
	valid_words)

import os

ANAGRAMS_FILE = './assets/anagrams.json'
FIVE_LETTER_WORDS_FILE = './assets/all_five_letter_words.txt'
BEST_WEIGHTS_FILE = './assets/wordle_weights.json'

default_known_anagrams = {}

def build_known_anagrams(alphabet, dictionary, known_anagrams={}):
	if os.path.exists(ANAGRAMS_FILE):
		return read_json_cache(ANAGRAMS_FILE)
	else:
		valid_words(alphabet, dictionary, known_anagrams)
		return known_anagrams


def get_all_five_letter_words(alphabet, dictionary, known_anagrams):
	if os.path.exists(FIVE_LETTER_WORDS_FILE):
		with open(FIVE_LETTER_WORDS_FILE, 'r') as f:
			all_five_letter_words = set([x.strip() for x in f.readlines()])
	else:
		all_five_letter_words = valid_words(alphabet, dictionary, known_anagrams)
		with open(FIVE_LETTER_WORDS_FILE, 'w') as f:
			[f.write(f"{x}\n") for c in all_five_letter_words]

	return all_five_letter_words

def write_known_anagrams(anagrams):
	write_json_cache(anagrams, ANAGRMS_FILE)