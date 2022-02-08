from WordleAI.Wordle_Solver import (
		try_it_out,
		output_best_weights
	)
from assets.WordleModels import (
		try_it_out,
		WordleInteractiveGame
	)

if __name__ == '__main__':
	try_it_out(game=WordleInteractiveGame())