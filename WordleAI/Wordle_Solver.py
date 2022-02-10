from collections import defaultdict
import json
import time
import random

from WordleAI import (
		get_letter_frequencies,
		logging,
		LetterType,
		letter_type_names,
		alpha_set,
		BEST_STARTING_WORDS

	)

from assets.WordleModels import (
		WordleGame,
		WordleTesterGame,
		WordleInteractiveGame,
		get_default_heuristics,
)

from utils import (
		write_json_cache,
		valid_words,
		valid_words_given_slots,
		total_permutations,
		print_monotonic as time_left,
		ordinal_suffix,
	)

from assets import (
	build_known_anagrams,
	get_all_five_letter_words,
	BEST_WEIGHTS_FILE,
	write_known_anagrams,
	build_known_anagrams,
	wordle_accepted_dictionary,
	)



RANDOM_SEED = 42069 # Nice ;)

letter_frequencies = get_letter_frequencies()
all_five_letter_words = get_all_five_letter_words()
known_anagrams = build_known_anagrams()

def get_optimal_guess(game, guesses, start_perms_threshold=1):
	logger = logging.getLogger('get_optimal_guess')
	letters_used = game.guessed_letters
	known_slots = game.known_word_slots
	known_letters = game.yellow_letters
	yellow_letter_slots = game.yellow_letter_slots
	heuristics = game.get_heuristics()

	logger.debug(f'Current Letters Used: {letters_used}')
	logger.debug(f'Current Known Slots: {known_slots}')
	logger.debug(f'Current Known Letters: {known_letters}')
	logger.debug(f'Current Known Yellow Letter Slots: {yellow_letter_slots}')
	
	
	letters_left = alpha_set.difference(letters_used)
	gray_letters = letters_used.difference(known_letters)

	logger.debug(f"Letters not used yet: {letters_left}")
	logger.debug(f"Letters known not in the word: {gray_letters}")
	
	turns_left = game.max_guesses - game.num_guesses

	logger.debug(f"Possible word permutations given only letters left: {total_permutations(letters_left)}")
	logger.debug(f"Possible word permutations given letters left and yellow/green letters: {total_permutations(letters_left.union())}")
	
	def multi_sort_info_gather(words,g): 
		
		def get_word_score(word):
			total = 0
			for heuristic in heuristics:
				hu = heuristics[heuristic]
				f = hu.get('function', lambda x: 0.0)
				w = hu.get('weight', 0.0)
				score = f(word) * w
				# logger.debug(f"Running {hu.get('name', 'UNKNOWN')} heuristic on word {word} => received score {score}")
				total += score
			return total
		
		def h(word):
			total_score = get_word_score(word)
			# logger.debug(f"total score for word {word} is {total_score}")
			return total_score
			
		res = [w for w in words if w not in g]
		# logger.debug(f"Words Given: {','.join(res)}")
		return sorted(res, key=h)
				  
	if turns_left in [game.max_guesses - i for i in range(start_perms_threshold)]: # start off with some good guesses to keep the overall permutations down later
		best_starting_moves = BEST_STARTING_WORDS.copy()
		ordered_best_options = [guess for guess in multi_sort_info_gather(best_starting_moves, guesses) if guess not in guesses]
		logger.debug(f"Best Options while choosing from defined list: {', '.join(ordered_best_options)}")
		return ordered_best_options[0]
	
	elif turns_left != 1 and len(known_letters) < 5: # still gathering info, guess most random valid word
		valid_guesses = valid_words(letters_left, wordle_accepted_dictionary, known_anagrams)
		logger.debug(f"showing {len(valid_guesses)} valid guesses from letters left: {letters_left}")

		if not valid_guesses:
			expanded_letters = letters_left.union(known_letters)
			valid_guesses = valid_words(expanded_letters, wordle_accepted_dictionary, known_anagrams)
			logger.debug(f"showing {len(valid_guesses)} valid guesses from letters left + yellow_letters: {expanded_letters}")
		ordered_best_options = multi_sort_info_gather(valid_guesses, guesses)
		game.add_learnable_guesses(ordered_best_options)
		logger.debug(f"Best Options while choosing from permutations list: {', '.join(ordered_best_options)}")
		return ordered_best_options[0]
	
	else: # we should have an answer by now
		
		possible_ending_words = valid_words_given_slots(known_slots, known_letters, wordle_accepted_dictionary)
		# log.debug(f"known_letters: {}")
		if not possible_ending_words or len(known_letters) < 5:
			possible_ending_words = valid_words_given_slots(known_slots, letters_left.union(known_letters), wordle_accepted_dictionary)
		
		def h(word):
			total_letters_in_word = sum([1 for letter in set(word) if letter in known_letters])
			letters_in_correct_spot = sum([1 for i, letter in enumerate(word) if known_slots[i] == letter])
			return sum([total_letters_in_word, letters_in_correct_spot])
		
		def get_best_word_order(possibilities):
			return sorted(possibilities, key=h, reverse=True)
			
		best_word_order = get_best_word_order(possible_ending_words)
		logger.debug(f"Best Options for final word: {', '.join(best_word_order)}")
		
		try:
			return best_word_order[0]
		
		except:
			raise Exception(f"No possible ending words found: {game.game_state}")


def run_game(word=None, game=None, start_perms_threshold=1, try_write_known_anagrams=False):
	logger = logging.getLogger('run_game')
	tester = game

	if word and not tester:
		tester = WordleTesterGame(word)
	elif not tester:
		tester = WordleInteractiveGame

	guesses = []
	while not tester.is_game_over():
		best_guess = get_optimal_guess(tester, guesses, start_perms_threshold=start_perms_threshold)
		logger.debug(f"Guessing {best_guess}")
		tester.make_guess(best_guess)
		guesses.append(best_guess)
	
	if tester.is_game_won():
		logger.debug("Yay! It did the thing! Now Try a different word..")

	else:
		logger.debug("welp.. that didn't work. Back to the drawing board..")
		logger.debug(tester.game_state)
			
	if try_write_known_anagrams:
		logger.info(f"Writing out known anagrams")
		write_known_anagrams(known_anagrams)

	return guesses, tester.is_game_won()


all_words = list(all_five_letter_words)

def run_test_and_update_weights(word, heuristics, start_perms_threshold=0, r=0.1):
	logger = logging.getLogger('run_test_and_update_weights')
	game = WordleTesterGame(word)
	game.set_heuristic_weights(heuristics)
	guesses_array = []
	did_win = False
	
	try:
		guesses_array, did_win = run_game(game=game, start_perms_threshold=start_perms_threshold, try_write_known_anagrams=True)
	except Exception as e:
		logger.warning(f"Threw exception {e} on word {word}")
		did_win = False
		
	yt = 0 if did_win else 1

	logger.debug(f"""{f"We got {word} in {game.num_guesses} guesses ヾ(-_- )ゞ" if did_win else f"We didn't get {word} (ಥ⌣ಥ)"}""")

	def update(expected_value, w):
		for h in heuristics:
			hu = heuristics[h]
			w_i = hu['weight']
			x_i = hu['function'](w)
			w_i_new = w_i + r*(expected_value - yt)*x_i
			hu['weight'] = w_i_new
		
	update(0,word)
		
	for w in game.get_learnable_guesses():
		update(1, w)
	
	return did_win, game.num_guesses, heuristics
		
def get_printable_weights(heuristics, outer_join_key='\n\t', inner_join_key=' : '):
	return outer_join_key + outer_join_key.join([inner_join_key.join([k, str(v['weight'])]) for k, v in heuristics.items()])

def learn_thresholds_and_weights(permutation_thresholds=[2,3,4], decay_rates=[1.0, 0.1, 0.01, 0.001]):
	logger = logging.getLogger('learn_thresholds_and_weights')
	timer = time.monotonic

	best_thresh_decay = defaultdict(lambda: 0)
	ending_heuristic_by_params = {}

	shuffled_words = all_words.copy()
	random.Random(RANDOM_SEED).shuffle(shuffled_words)
	mid_idx = len(shuffled_words) // 2
	training_set = shuffled_words[:mid_idx]
	training_size = len(training_set)
	testing_set = shuffled_words[mid_idx:]
	testing_size = len(testing_set)
	base_heuristics = get_default_heuristics()
	logger.info(f"Initializing base weights")
	random.seed(RANDOM_SEED)
	for x in base_heuristics:
		if x.lower() != 'bias':
			base_heuristics[x]['weight'] = random.random()
		
	logger.debug(f"Default weights: {get_printable_weights(base_heuristics)}")

	logger.info("Beginning Learning!")
	#range(WordleGame.max_guesses - 1):	
	for perm_thresh in permutation_thresholds:

		for d in decay_rates:
			logger.info(f"started training on permutation threshold {perm_thresh} and decay_rate {d}")
			r_0 = 0.1
			heuristics = base_heuristics.copy()
			times_elapsed = 0
			total_wins_this_round = 0
			guess_len_dict = defaultdict(lambda: 0)
			for idx, word in enumerate(training_set):
				logger.debug(f"Running {idx + 1}{ordinal_suffix(idx + 1)} test on word {word}")
				logger.info(f"{total_wins_this_round} W | {idx - total_wins_this_round} L | {training_size - idx} Remaining")

				r = r_0 / (1 + d*idx)
				
				s = timer()
				did_win, num_guesses, heuristics = run_test_and_update_weights(word, heuristics, perm_thresh, r)
				delta = timer() - s
				guess_len_dict[num_guesses] += 1

				total_wins_this_round += 1 if did_win else 0
				
				times_elapsed += delta
				avg_time_per_run = times_elapsed / (idx + 1)
				runs_left = training_size - (idx + 1 + 1)
				time_left_seconds = avg_time_per_run * runs_left

				t = time_left(time_left_seconds)

				logger.info(f"Finished training on {word}, completed in {delta:.2f} seconds")
				logger.info(f"{' | '.join([f'{key} : {val}' for key, val in guess_len_dict.items()])}")
				logger.info(f"estimated time left in stage: {t}")
				logger.debug(f"new weights: {get_printable_weights(heuristics)}")
				
				if (idx + 1) % 100 == 0: logger.info(f"{(idx / training_size):.2%} of the way done training!")
				
			ending_heuristic_by_params[(perm_thresh, d)] = heuristics
			logger.info(f"final heuristics for permutation_threshold {perm_thresh} and decay rate {d}")
			logger.info(f"Writing out known anagrams")
			write_known_anagrams(known_anagrams)
			
			logger.info(f"{get_printable_weights(heuristics)}")
	
	logger.info("Finally done training. Now to testing??")
	
	for (thresh, d), heuristics in ending_huristic.items():
		logger.info(f"started testing on permutation threshold {thresh} and decay_rate {d}")
		logger.info(f"Heuristics: {get_printable_weights(heuristics)}")
		for idx, word in enumerate(testing_set):
			logger.info(f"Running {idx + 1}th test on word {word}")
			game = WordleTesterGame(word)
			game.set_heuristic_weights(heuristics)
			did_win = False
			try:
				guesses_array, did_win = run_game(game=game, permutations_thresholds=permutations_thresholds)
			except Exception as e:
				logger.warning(f"Threw exception {e} on word {word}")
				did_win = False
			logger.debug(f"Did we win? {did_win}")
			best_thresh_decay[(thresh, d)] += 1 if did_win else 0
			
			if idx + 1 % 100 == 0: logger.info(f"{(idx / testing_size):.2%} of the way done testing!")
			
	return ending_heuristic_by_params, best_thresh_decay

def output_best_weights():
	# try:
	logger = logging.getLogger('output_best_weights')
	learned_heuristics, best_params = learn_thresholds_and_weights()

	best_thresh, best_decay = max(best_params, key=best_params.get)
	best_heuristic = learned_heuristics[best_params]
	logger.info(f"The best hyper-params are:\nThreshold: {best_thresh}\nDecay Rate: {best_decay}")
	join_key = '\n\t'
	logger.info(f"The Best Heuristic weights are:\n\t{join_key.join([':'.join([name, h['weight']]) for name, h in best_heuristic.items()])}")   
	
	logger.info(f"Writing Best Heuristic Weights to '{BEST_WEIGHTS_PATH}'")
	best_heuristic_weights = {}
	for k in best_heuristic:
		best_heuristic_weights[k] = best_heuristic[k]['weight']
	write_json_cache(best_heuristic_weights, BEST_WEIGHTS_PATH)

	# except KeyboardInterrupt:
	# 	logger.info(f"Received Exit")
	# 	do_write = input('Should I write known anagrams to disk? ')
	# 	do_write = do_write or 'n'
	# 	if do_write[0].lower() == 'y':
	# 		write_known_anagrams(known_anagrams)


if __name__ == '__main__':
	output_best_weights()