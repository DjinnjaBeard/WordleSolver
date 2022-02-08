import enchant as e
import logging
from enum import Enum, auto
import random
from collections import defaultdict
from itertools import groupby
from utils import dict_by_length

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

random.seed(42069)

english_dictionary = e.Dict("en_US")

class LetterType(Enum):
	GRAY = 1
	GY = 1
	A = 1
	YELLOW = 2
	Y = 2
	GREEN = 3
	GN = 3
	N = 3

letter_type_names = [name for name in LetterType.__members__]

letter_type_aliases = {
	enum_group.name: list(aliases) 
	for 
		enum_group, aliases 
	in groupby(
		LetterType.__members__, 
		lambda k: LetterType.__members__[k]
	)}

letters_by_length = dict(sorted(dict_by_length([t.lower() for t in letter_type_names]).items(), key=lambda x: x[0], reverse=True))

default_letter_frequencies = {
		'a': 20.5,
		'b': 2.7,
		'c': 3.6,
		'd': 3.3,
		'e': 10.0,
		'f': 1.6,
		'g': 2.6,
		'h': 3.1,
		'i': 6.1,
		'j': 0.4,
		'k': 2.1,
		'l': 5.6,        
		'm': 3.1,
		'n': 5.2,
		'o': 6.6,
		'p': 3.0,
		'q': 0.2,
		'r': 7.2,
		's': 5.6,
		't': 5.6,
		'u': 4.4,
		'v': 1.1,
		'w': 1.6,
		'x': 0.4,
		'y': 3.8,
		'z': 0.6        
}

BEST_STARTING_WORDS = [
    'react',
    'adieu',
    'later',
    'sired',
    'tears',
    'alone',
    'arise',
    'about',
    'atone',
    'irate',
    'snare',
    'cream',
    'paint',
    'worse',
    'sauce',
    'anime',
    'prowl',
    'roast',
    'drape',
    'media'
]

alpha_set = set(default_letter_frequencies.keys())

def get_letter_frequencies(smoothing_amt=0):
	new_frequencies = default_letter_frequencies.copy()
	total_prob = sum([new_frequencies[i] for i in new_frequencies])
	for l, new_freq in new_frequencies.items():
		new_freq /= total_prob
		if smoothing_amt:
			new_freq = (new_freq + smoothing_amt)/(WordleGame.word_length + smoothing_amt*len(letter_frequencies))
		new_frequencies[l] = new_freq
		
	return new_frequencies