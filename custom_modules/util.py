# -*- coding: utf-8 -*-

import six
import boto3
import json
import os
from random import randrange

from custom_modules import data


# CLEARS THE BOARD PLACING 0 IN EVERY POSITION TO START A NEW GAME
def clear_board():
    board = [[data.EMPTY_CODE for x in range(data.BOARD_WIDTH)] for y in range(data.BOARD_HEIGHT)]
    return board

# VALIDATES IF THE POSITION WHERE A PIECE WISHES TO BE PLACED IS VALID
def validate_position(piece, start, end):
    if start == end:
        print(data.SAME_START_AND_END)
        return {"is_legal": False, "msg": data.SAME_START_AND_END}
    elif start[0] > 9 or end[0] > 9 or start[1] > 9 or end[1] > 9:
        print(data.OUT_OF_BOARD_RANGE)
        return {"is_legal": False, "msg": data.OUT_OF_BOARD_RANGE}
    elif start[0] != end[0] and start[1] != end[1]:
        print(data.NOT_STRAIGHT)
        return {"is_legal": False, "msg": data.NOT_STRAIGHT}
    elif start[0] == end[0]:
        distance = abs(start[1] - end[1]) + 1
        if distance != data.PIECES[piece]["size"]:
            return {"is_legal": False, "msg": data.WRONG_SIZE.format(piece_size=data.PIECES[piece]["size"], distance=distance)}
        else:
            return {"is_legal": True, "msg": data.LEGAL_PLACEMENT}
    elif start[1] == end[1]:
        distance = abs(start[0] - end[0]) + 1
        if distance != data.PIECES[piece]["size"]:
            return {"is_legal": False, "msg": data.WRONG_SIZE.format(piece_size=data.PIECES[piece]["size"], distance=distance)}
        else:
            return {"is_legal": True, "msg": data.LEGAL_PLACEMENT}
    else:
        return {"is_legal": False, "msg": data.UNKNOWN_ERROR}

# VALIDATES IF THE SQUARES WHERE data.PIECES WISHES TO BE PLACED ARE EMPTY
def validate_board_square(board, piece, start, end):
    for x in range(start[0], end[0] + 1):
        for y in range(start[1], end[1] + 1):
            if board[x][y] != data.EMPTY_CODE:
                return {"is_legal": False, "msg": data.BOARD_SQUARE_CONFLICT}

    return {"is_legal": True, "msg": data.BOARD_SQUARE_CONFLICT}


# CHECKS IF IT IS POSSIBLE TO PLACE A PIECE IN A POSITION
def validate_placement(board, piece, start, end):
    print("Validating placement...")
    is_legal_position = validate_position(piece, start, end)
    print(is_legal_position)
    if is_legal_position.get("is_legal", False):
        is_legal_square = validate_board_square(board, piece, start, end)
        if is_legal_square.get("is_legal", False):
            return {"is_legal": True, "msg": data.LEGAL_PLACEMENT}
        else:
            return is_legal_square
    else:
        return is_legal_position


# PLACES A PIECE IN THE BOARD
def place_piece(board, piece, start, end):
    is_valid_placement = validate_placement(board, piece, start, end)
    if is_valid_placement["is_legal"]:
        for x in range(start[0], end[0] + 1):
            for y in range(start[1], end[1] + 1):
                board[x][y] = data.PIECES.get(piece).get("code")
        return {"is_legal": True, "msg": data.LEGAL_PLACEMENT, "board": board}

    else:
        return {"is_legal": False, "msg": is_valid_placement["msg"], "board": board}


# TRANSLATES THE SLOT CODE INTO A VECTOR
def get_square(slot_code):
    print("Getting square from slot code")
    square = [ord(slot_code.split("_")[0]) - ord("A"), int(slot_code.split("_")[1]) - 1]
    print("Square: " + str(square))
    return square

def get_slot_code(square):
    slot_code = data.ROWS[square[0]] + data.COLUMNS[square[1]]
    return slot_code

def get_ship_id(ship):
    ship_id = ship.replace(" ", "_").lower()
    return ship_id

# GETS SHIP NAME FROM CODE
def get_ship_from_code(code):
    for key, value in data.PIECES.items():
        if value.get("code") == code:
            return key
    return None

# GENERATES A RANDOM SQUARE TO PLACE A PIECE OR FOR COMPUTER ATTACK
def get_random_square():
    square = [randrange(10), randrange(10)]
    return square

# GETS A RANDOM ORIENTATION (HORIZONTAL = 0 AND VERTICAL = 1) TO PLACE A PIECE
def get_random_orientation():
    return randrange(2)


# CALCULATES RANDOM PIECE END POSITION BASED ON ITS SIZE, THE START POSITION AND THE ORIENTATION
def get_random_end(size, start, orientation):
    return [start[0] if orientation == 0 else start[0] + size - 1, start[1] if orientation == 1 else start[1] + size - 1]


# RANDOMLY CONFIGURES THE COMPUTERS BOARD
def get_random_board():
    board = clear_board()
    for ship, info in data.PIECES.items():
        print("Randomly placing " + ship)
        successful_random_placement = False
        while not successful_random_placement:
            random_start = get_random_square()
            print("Random start: " + str(random_start))
            random_orientation = get_random_orientation()
            print("Random orientation: " + str(random_orientation))
            random_end = get_random_end(info.get("size"), random_start, random_orientation)
            print("Random end: " + str(random_end))
            random_placement = place_piece(board, ship, random_start, random_end)
            successful_random_placement = random_placement.get("is_legal")
        print(ship + " randomly placed successfully")

    return board


def attack_square(square, board):
    print("Attempting attack to square " + str(square) + " in board " + str(board))
    target_square = board[square[0]][square[1]]
    if target_square == data.EMPTY_CODE:
        board[square[0]][square[1]] = data.MISS_CODE
        return {"is_legal": True, "hit": False, "msg": data.MISS_MSG + data.ATTACK_SQUARE + get_slot_code(square) + ". ", "board": board}
    elif target_square == data.MISS_CODE:
        return {"is_legal": False, "hit": False, "msg": data.REPEAT_ATTACK_SQUARE_MSG, "board": board}
    elif target_square % 10 == data.HIT_CODE:
        return {"is_legal": False, "hit": False, "msg": data.REPEAT_ATTACK_SQUARE_MSG, "board": board}
    else:
        # TODO CHECK IF SHIP SUNK
        hit_ship_name = get_ship_from_code(board[square[0]][square[1]])
        board[square[0]][square[1]] += data.HIT_CODE
        return {"is_legal": True, "hit": True, "msg": data.HIT_MSG + hit_ship_name + data.ATTACK_SQUARE + get_slot_code(square) + "! ", "board": board}


def opponent_attack_square(board):
    valid_attack = False
    while not valid_attack:
        target_square = get_random_square()
        opponent_attack = attack_square(target_square, board)
        valid_attack = opponent_attack.get("is_legal")

    return opponent_attack
