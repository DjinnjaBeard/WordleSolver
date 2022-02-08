from WordleAI import (
		LetterType,
		letter_type_names,
		logging,
		get_letter_frequencies,
		english_dictionary,
		defaultdict,
		letters_by_length
	)



letter_frequencies = get_letter_frequencies()

_default_heuristics = lambda **kwargs : {
		'Duplicate Letters': {
			'function': lambda word: len(word) - len(set(word)), 
			'weight': 0.75
		},
		'Reconfirming Gray Letters': {
			'function': lambda word: sum([1 for letter in word if letter in kwargs.get('gray_letters', set())]), 
			'weight': 5.0
		},
		'Reconfirming Yellow Slots': {
			'function': lambda word: sum([1 for idx, letter in enumerate(list(word)) if letter in kwargs.get('yellow_letter_slots', defaultdict(set))[idx]]), 
			'weight': 1.0
		},
		'Reconfirming Green Letters': {
			'function': lambda word: sum([1 for idx, letter in enumerate(list(word)) if letter == kwargs.get('known_slots', [None] * idx)[idx]]), 
			'weight': 1.0
		},
		'Aggregate Letter In-Frequency': {
			'function': lambda word: 1 - sum([letter_frequencies.get(letter, 0.0) for letter in word]) / len(word), 
			'weight': 3.0
		},
		'Bias': {
			'function': lambda word: 1,
			'weight': 1.0
		},}

def get_default_heuristics(): 
	return _default_heuristics(
		gray_letters=set(), 
		yellow_letter_slots=defaultdict(set), 
		known_slots=[None] * 5)

class WordleGame:
	max_guesses = 6
	word_length = 5
	
	def __init__(self, heuristics=get_default_heuristics(), dictionary=english_dictionary):
		self.logger = logging.getLogger('WordleGame')
		self.guessed_letters = set()
		self.yellow_letters = set()
		self.known_word_slots = [None] * 5
		self.game_state = []
		self.yellow_letter_slots = defaultdict(set)
		self.heuristics = get_default_heuristics()
		self.set_heuristic_weights(heuristics)
		self.dictionary=dictionary
	
	@staticmethod
	def is_valid_wordle(word, dictionary):
		return (dictionary.check(word.lower())
			and word.isalpha() 
			and len(word) == WordleGame.word_length)
		
		
	def make_guess(self, guess):
		self.logger.debug(f'Attempting to update game state with word: {guess}')
		if self.is_valid_wordle(guess, self.dictionary) and not self.is_game_over():
			self._update_game_state(guess.lower())
		else:
			raise ValueError(f"{guess} is an invalid guess")
			
		return (self.game_state, self.guessed_letters)
	
	def _update_game_state(self, guess):
		self.logger.debug(f'Updating Game State with guess: {guess}')
		self.guessed_letters.update(guess)
		self.logger.debug(f'New guessed letters: {self.guessed_letters}')
		guess_result = self.get_guess_result(guess)
		self.game_state.append(guess_result)
		
		for idx, (letter, letter_type) in enumerate(guess_result):
			self.logger.debug(f'Result data for letter {letter} @ idx {idx}: {letter_type.name}')
			match letter_type:
				case LetterType.YELLOW:
					self.logger.debug('Letter was marked as yellow')
					self.yellow_letters.add(letter)
					self.yellow_letter_slots[idx].add(letter)
				case LetterType.GREEN:
					self.logger.debug('Letter was marked as green')
					self.known_word_slots[idx] = letter
					self.yellow_letters.add(letter)
				case _:
					self.logger.debug('Letter was marked as gray')
					continue

	def get_heuristics(self):
		new_heuristics = _default_heuristics(
			gray_letters=self.guessed_letters.difference(self.yellow_letters), 
			yellow_letter_slots=self.yellow_letter_slots, 
			known_slots=self.known_word_slots)
		
		old_heuristics = self.heuristics
		self.heuristics = new_heuristics
		self.set_heuristic_weights(old_heuristics)
		return self.heuristics
	
	def set_heuristic_weights(self, new_heuristics):
		for h in self.heuristics:
			self.heuristics[h]['weight'] = new_heuristics[h]['weight']
	
	def get_guess_result(self, guess):
		return []
	
	def is_game_won(self):
		return all([x for x in self.known_word_slots])
	
	def is_game_lost(self):
		return len(self.game_state) >= self.max_guesses
	
	def is_game_over(self):
		return self.is_game_won() or self.is_game_lost()


class WordleTesterGame(WordleGame):
	
	@staticmethod
	def play_tester_game():
		wordle = ''
		while not wordle:
			word = input("What is the wordle, birdle?").lower()
			if WordleGame.is_valid_wordle(word, self.dictionary):
				wordle = word
			else:
				print(f"{word} is not a valid wordle!")
				
		tester = WordleTesterGame(wordle)
		while not tester.is_game_over():
			guess = input('Whats your guess?')
			game_state, letters_guessed = tester.make_guess(guess)
			current_state = game_state[-1]
			
			if tester.is_game_won():
				print(f"That's it! '{guess}' was the word!")
				break
				
			print(f"Game State: {current_state}")
			print(f"Letters guessed: {sorted(letters_guessed)}")

			
	def __init__(self, word, dictionary=english_dictionary, heuristics=get_default_heuristics()):
		if not WordleGame.is_valid_wordle(word, dictionary):
			raise ValueError(f"{word} is not a valid wordle")
		super().__init__(dictionary=dictionary, heuristics=heuristics)
		self.logger = logging.getLogger('WordleGame')
		self.word = word.lower()
	
	def get_guess_result(self, guess):
		result = []
		for idx, letter in enumerate(guess):
			if self.word[idx] == letter:
				result.append((letter, LetterType.GREEN))
			elif letter in self.word:
				result.append((letter, LetterType.YELLOW))
			else:
				result.append((letter, LetterType.GRAY))
		return result



class WordleInteractiveGame(WordleGame):
	def __init__(self, dictionary=english_dictionary, heuristics=get_default_heuristics()):
		super().__init__(dictionary=dictionary, heuristics=heuristics)
		self.logger = logging.getLogger('WordleGame')
		
	@staticmethod
	def _parse_guess(input_string):
		logger = logging.getLogger('_parse_guess')
		modded_string = ''.join(input_string.split()).lower()
		logger.debug(f"parsing {input_string}")
			
		returned = []
		if not input_string:
			return returned
		
		for length, keys in letters_by_length.items():
			logger.debug(f"Trying length: {length}")
			if len(modded_string) >= length:
				potential_parse = modded_string[:length]
				logger.debug(f"Trying Potential parse of {modded_string} on inputs {keys}")
				if potential_parse in keys:
					logger.debug(f"Found potential parse: {potential_parse}")
					modded_string = modded_string[length:]
					returned.append(LetterType[potential_parse.upper()])
					returned += WordleInteractiveGame._parse_guess(modded_string)
					return returned

		raise ValueError(f"{input_string} does not parse")
			
	def get_guess_result(self, guess):
		successful_parse = False
		while not successful_parse:
			try:
				row_input = input(f'What\'s the result of guessing {guess}?')
				guess_result = [(guess[idx], color) for idx, color in enumerate(WordleInteractiveGame._parse_guess(row_input))]
				successful_parse = True
			except ValueError as e:
				logger.warning(e)


		self.logger.debug(f'Guess Result Parsed as: {", ".join([" : ".join([letter, color.name]) for letter, color in guess_result])}')
		return guess_result