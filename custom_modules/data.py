# -*- coding: utf-8 -*-


# SHIP CODES AND SIZES
SHIPS = ["Patrol Boat", "Battleship", "Carrier", "Destroyer", "Submarine"]
PIECES = {"patrol_boat": {"size": 2, "code": 110}, "battleship": {"size": 4, "code": 120}, "carrier": {"size": 5, "code": 130}, "destroyer": {"size": 3, "code": 140}, "submarine": {"size": 3, "code": 150}}
MAX_HITS = 17


ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
COLUMNS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# BOARD SETTINGS
BOARD_WIDTH, BOARD_HEIGHT = 10, 10
CURRENT_GAMES_TABLE = "CURRENT_GAMES_TABLE"
BOARD_IMAGES_BUCKET = "BOARD_IMAGES_BUCKET"

# BOARD SLOT CODES
EMPTY_CODE = 0
MISS_CODE = -1
HIT_CODE = 1

# ILLEGAL MOVES AND PLACEMENT ERROR
LEGAL_PLACEMENT = "Legal placement. "
LEGAL_SQUARES = "Legal squares. "
UNKNOWN_ERROR  = ("Unknown error. ")
NOT_STRAIGHT = "Ship must be placed vertically or horizontally. "
SAME_START_AND_END = "Start and end square cannot be the same. "
OUT_OF_BOARD_RANGE = "Placement out of board range. "
WRONG_SIZE = "Wrong size. The piece you wish to place has size {piece_size}, while you placed in a distance of {distance} squares in the board!. "
BOARD_SQUARE_CONFLICT = "There is already a piece in one of these squares.. "



MISS_MSG = "missed "
REPEAT_ATTACK_SQUARE_MSG = "You already attacked this square. "
HIT_MSG = "hit a ship "
SUNK_MSG = "sunk the "
ATTACK_SQUARE = "in square "
YOU = "You "
OPPONENT = "Your opponent "

USER_WON_GAME = "Congratulations! You won the game!"
OPPONENT_WON_GAME = "Too bad! Your opponent won the game!"

WELCOME_MESSAGE = ("Welcome to Battleship! Let's play a game.  ")
HELP_MESSAGE = ("What would you like to do? ")
EXIT_SKILL_MESSAGE = ("Até a próxima ")
ERROR_MESSAGE = ("Ups! We had a problem. Can you repeat?")
UNEXPECTED_ERROR  = ("Unexpected error. ")
FALLBACK_ANSWER = ("Ups! We had a problem. Can you repeat?")


SAMPLE_RESPONSE = ["Exemplo 1 ", "Exemplo 2 "]

LIST_SHIPS_RESPONSE = ["The ships are: "]

PLACE_PIECE_RESPONSE = ["Where would you like to place the ", "In which position you want to place the "]
PLACE_PIECE_SIZE = ["that has size ", "who's size is ", "with size "]
ILLEGAL_PLACEMENT = ["Illegal placement. ", "That is not a valid placement. "]

BOARD_READY = ["The board is ready to start the game. ", "The board is setup to start the game. "]
ATTACK = ["Which position do you wish to attack? ", "What position would you like to attack? "]

AND = ("and")
