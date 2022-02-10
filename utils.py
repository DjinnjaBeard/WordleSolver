from itertools import product
import json

class PrintColors:
	BLACK = '\u001b[40;1m'
	GREEN = '\u001b[42;1m'
	YELLOW = '\u001b[43;1m'
	RESET = '\u001b[0m'

def write_json_cache(c, p):
	jstr = json.dumps(c)
	with open(p, 'w') as fp:
		fp.write(jstr)
		
def read_json_cache(p):
	with open(p, 'r') as fp:
		return json.load(fp)

total_permutations = lambda l: len(l)**5

permute_tuples = lambda options, num_repeats: [*product(options, repeat=num_repeats)]

def print_monotonic(time_in_seconds):
	hours = time_in_seconds // 3600
	minutes = time_in_seconds % 3600 // 60
	seconds = time_in_seconds % 60 // 1
	return f"{hours}h:{minutes}m:{seconds}s"

def ordinal_suffix(num):
	match num % 10:
		case 1 if num != 11:
			return 'st'
		case 2:
			return 'nd'
		case 3:
			return 'rd'
		case _:
			return 'th'
					

def dict_by_length(words):
	ret = {}
	for word in words:
		ret.setdefault(len(word), []).append(word)
	return ret


def valid_words(letters, dictionary, known_anagrams):
	avail_letters = tuple(letters)
	if avail_letters in known_anagrams:
		return known_anagrams[str(avail_letters)]
	else:
		all_ana = permute_tuples(avail_letters, 5)
		words = [''.join(list(word)) for word in all_ana if dictionary.check(''.join(list(word)))]
		known_anagrams[str(avail_letters)] = words
		return words

def valid_words_given_slots(known_slots, known_letters, dictionary):
	slots_left = known_slots.count(None)
	possible_letters = permute_tuples(known_letters, slots_left)
	possible_words = []
	for combo in possible_letters:
		c = list(combo)
		possible_word = ''
		for slot in known_slots:
			possible_word += slot if slot else c.pop()
		possible_words.append(possible_word) if dictionary.check(possible_word) else None
	return possible_words
