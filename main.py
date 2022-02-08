from WordleAI.Wordle_Solver import (
		run_game,
		output_best_weights
	)
from WordleAI import letter_type_aliases, logging
from assets.WordleModels import (
		WordleInteractiveGame
	)

if __name__ == '__main__':
	n_line='\n'
	tab='\t'
	welcome_message = f"""
Welcome to the wordle solver!

This is currently being developed,
and hopefully it will be improved over time 
as I continue to hone the weights and heuristics.

An interactive wordle AI will begin 
prompting you for responses to a word.

You should type this word into your 
wordle application, and enter the 
response colors into the prompt

Acceptable Entries (case insensitive):
{n_line.join([f"{tab + name}: {[','.join(aliases)]}" for name, aliases in letter_type_aliases.items()])}
	"""
	print(welcome_message)
	print()
	again_str = ''
	while(not input(f"Press Enter To Play{again_str}. Any other input to quit.")):
		again_str = " Again"
		run_game(game=WordleInteractiveGame(), start_perms_threshold=3)