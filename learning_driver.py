from WordleAI.Wordle_Solver import output_best_weights
from WordleAI import logging

if __name__ == '__main__':
	logging.getLogger('learn_thresholds_and_weights').setLevel(logging.DEBUG)
	logging.getLogger('run_test_and_update_weights').setLevel(logging.DEBUG)
	# logging.getLogger('WordleGame').setLevel(logging.DEBUG)
	output_best_weights()