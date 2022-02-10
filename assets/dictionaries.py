from collections import defaultdict
import os

class SimpleDict():

	parse_word = lambda word: ''.join([letter for letter in word if letter.isalpha()])

	@staticmethod
	def initialize_words(d, file):
		if os.path.exists(file):
			with open(file, 'r') as fp:
				for line in fp.readlines():
					word = SimpleDict.parse_word(line)
					d.add(word)


	def __init__(self, word_file='', words_list=[]):
		self._d = set()
		if word_file:
			self.initialize_words(self._d, word_file)
			self.words_list = list(self._d)
		elif words_list:
			self.words_list = words_list.copy()
			self._d.update([SimpleDict.parse_word(word) for word in words_list])
		else:
			raise ValueError(f"Cannot create dictionary with empty word file and word list")

	def check(self, word):
		return word in self._d