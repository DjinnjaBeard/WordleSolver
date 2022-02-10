from assets import (
	wordle_answer_dictionary, 
	wordle_accepted_dictionary,
	)

from assets.dictionaries import SimpleDict

from WordleAI import (
	LetterType, 
	base_letter_types,
	logging,
	color_mapping,
	)

from utils import (
	permute_tuples, 
	PrintColors,
	print_monotonic
	)

import math
import time

logger = logging.getLogger('WordleStatistics')
timer = time.monotonic

printable_perm = lambda word_perm : "".join([f'{color_mapping[t]}{letter}' for letter, t in word_perm]) + PrintColors.RESET

def test():
	dictionary = SimpleDict(words_list=wordle_answer_dictionary.words_list)
	current_possible_words = dictionary.words_list.copy()
	current_word = current_possible_words.pop()

	letters_in_slots = [None] * len(current_word)
	letters_not_in_slots = [set()] * len(current_word)
	known_letters_in_word = set()
	letters_not_in_word = set()

	for i in range(6):
		
		word_perm = None
		
		while not word_perm:
			current_word = current_possible_words.pop()
			
			s = timer()
			word_perms = generate_word_permutations(current_word)
			delta = timer() - s
			
			logger.debug(f'got {word_perms}')
			logger.debug(f"Took {print_monotonic(delta)} to run generate_word_permutations({current_word})")

			word_perm = next(word_perms, None)


		letters_in_slots_copy = letters_in_slots.copy()
		letters_not_in_slots_copy = letters_not_in_slots.copy()
		known_letters_in_word_copy = known_letters_in_word.copy()
		letters_not_in_word_copy = letters_not_in_word.copy()
		current_possible_words_copy = current_possible_words.copy()

		next_words = []

		s = timer()
		while not next_words:
			next_words = words_given_permutation(word_perm, dictionary,
				letters_in_slots=letters_in_slots_copy,
				letters_not_in_slots=letters_not_in_slots_copy,
				known_letters_in_word=known_letters_in_word_copy,
				letters_not_in_word=letters_not_in_word_copy)

			next_word = next(next_words, None)
			if not (next_word or next_word == current_word):
				next_words = []
				word_perm = next(word_perms, None)
				letters_in_slots_copy = letters_in_slots.copy()
				letters_not_in_slots_copy = letters_not_in_slots.copy()
				known_letters_in_word_copy = known_letters_in_word.copy()
				letters_not_in_word_copy = letters_not_in_word.copy()
				current_possible_words_copy = current_possible_words.copy()

		delta = timer() - s
		logger.debug(f"Took {print_monotonic(delta)} to run collect next word from {current_word} to {next_word}")
		new_d_list = dictionary.words_list.copy()
		new_d_list.remove(current_word)
		dictionary = SimpleDict(words_list=new_d_list)

		letters_in_slots = letters_in_slots_copy
		letters_not_in_slots = letters_not_in_slots_copy
		known_letters_in_word = known_letters_in_word_copy
		letters_not_in_word = letters_not_in_word_copy
		current_possible_words = current_possible_words_copy

		logger.info(f'Finished run on :{printable_perm(word_perm)}')
		current_word = next_word




def entropy(word, dictionary=wordle_accepted_dictionary):
	num_words = len(dictionary.words_list)
	entropies = []
	for word_perm in generate_word_permutations(word):
		possible_sub_words = words_given_permutation(word)
		p_x = len(possible_sub_words) / num_words
		l_p_x = - math.log(p_x, 2)

		entropies.append(p_x * l_p_x)

	return sum(entropies)
	

def generate_word_permutations(word):
	logger = logging.getLogger('generate_word_permutations')
	logger.debug(f'Permuting word: {word}')
	possible_letter_types = permute_tuples(base_letter_types, len(word))
	logger.debug(f'Generated {len(possible_letter_types)} permutations')
	# logger.debug(res)
	yield from ([(letter, p) for letter, p in zip(word, perm)] for perm in possible_letter_types)



def words_given_permutation(word_perm, dictionary, **kwargs):
	logger = logging.getLogger('words_given_permutation')

	letters_in_slots = kwargs.get('letters_in_slots', [None] * len(word_perm))
	letters_not_in_slots = kwargs.get('letters_not_in_slots', [set()] * len(word_perm))
	known_letters_in_word = kwargs.get('known_letters_in_word', set())
	letters_not_in_word = kwargs.get('letters_not_in_word', set())
	all_possible_words = kwargs.get('all_possible_words', dictionary.words_list)

	if all(letter_type == LetterType.GREEN for letter, letter_type in word_perm):
		return [word]

	word = ''.join(letter for letter, letter_type in word_perm)

	for letter_idx, (letter, letter_type) in enumerate(word_perm):
		match letter_type:
			case LetterType.GRAY:
				if (word.count(letter) == 1 or 
					all([letter != l or 
						(letter == l and 
						 word_perm[i + 1][1] == LetterType.GRAY) 
						for i, l in enumerate(word[idx+1:])])): 
					letters_not_in_word.add(letter)
				else: 
					letters_not_in_slots[letter_idx].add(letter)
			case LetterType.YELLOW:
				known_letters_in_word.add(letter)
				letters_not_in_slots[letter_idx].add(letter)
			case LetterType.GREEN:
				letters_in_slots[letter_idx] = letter
				known_letters_in_word.add(letter)

	def filter_fn(w):
		logging.getLogger('filter_fn').debug(f'running filter fn on {w}')
		return all([(
			letter not in letters_not_in_word and 
			letter not in letters_not_in_slots[idx] and
			(letter == letters_in_slots[idx] if letters_in_slots else True))
			for idx, letter in enumerate(w)])

	# logger.debug(f'Begin filtering based on {printable_perm(word_perm)}')
	# s = timer()
	# filtered_list = list(filter(filter_fn, all_possible_words))
	# delta = timer() - s
	# logger.debug(f'filter took {print_monotonic(delta)} to run')

	yield from filter(filter_fn, all_possible_words)