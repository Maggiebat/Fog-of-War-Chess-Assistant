import random
# to be eventually replaced by actual AI
def dummy(moves_options, white_turn):
    if white_turn == True:
        print("The recommended move we suggest is", random.choice(moves_options))