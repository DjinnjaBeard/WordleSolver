from itertools import product
import json

def write_json_cache(c, p):
	jstr = json.dumps(c)
	with open(p, 'w') as fp:
		fp.write(jstr)
		
def read_json_cache(p):
	with open(p, 'r') as fp:
		return json.load(fp)

total_permutations = lambda l: len(l)**5

permute_tuples = lambda letters, num_repeats: [*product(letters, repeat=num_repeats)]


def valid_words(letters, dictionary, known_anagrams):
	avail_letters = list(letters)
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
