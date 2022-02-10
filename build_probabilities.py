from assets.WordleStatistics import test
from WordleAI import logging

if __name__ == '__main__':
	logging.getLogger('WordleStatistics').setLevel(logging.DEBUG)
	logging.getLogger('generate_word_permutations').setLevel(logging.DEBUG)
	test()