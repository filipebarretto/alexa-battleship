# -*- coding: utf-8 -*-

import six
import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')

# BOARD SETTINGS
BOARD_WIDTH, BOARD_HEIGHT = 10, 10
CURRENT_GAMES_TABLE = "CURRENT_GAMES_TABLE"

# BOARD SLOT CODES
EMPTY_CODE = 0
MISS_CODE = -1
HIT_CODE = 1


# SHIP CODES AND SIZES
PIECES = {"patrol_boat": {"size": 2, "code": 10}, "battleship": {"size": 4, "code": 11}, "carrier": {"size": 5, "code": 12}, "destroyer": {"size": 3, "code": 13}, "submarine": {"size": 3, "code": 14}}


# ILLEGAL MOVES AND PLACEMENT ERROR
LEGAL_PLACEMENT = "Legal placement. "
LEGAL_SQUARES = "Legal squares. "
UNKNOWN_ERROR  = ("Unknown error. ")
NOT_STRAIGHT = "Ship must be placed vertically or horiozntally. "
SAME_START_AND_END = "Start and end square cannot be the same. "
OUT_OF_BOARD_RANGE = "Placement out of board range. "
WRONG_SIZE = "Wrong size. The piece you wish to place has size {piece_size}, while you placed in a distance of {distance} squares in the board!. "
BOARD_SQUARE_CONFLICT = "There is already a piece in one of these squares.. "


# CLEARS THE BOARD PLACING 0 IN EVERY POSITION TO START A NEW GAME
def clear_board():
    board = [[0 for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
    return board

# VALIDATES IF THE POSITION WHERE A PIECE WISHES TO BE PLACED IS VALID
def validate_position(piece, start, end):
    if start == end:
        print(SAME_START_AND_END)
        return {"is_legal": False, "msg": SAME_START_AND_END}
    elif start[0] > 9 or end[0] > 9 or start[1] > 9 or end[1] > 9:
        print(OUT_OF_BOARD_RANGE)
        return {"is_legal": False, "msg": OUT_OF_BOARD_RANGE}
    elif start[0] != end[0] and start[1] != end[1]:
        print(NOT_STRAIGHT)
        return {"is_legal": False, "msg": NOT_STRAIGHT}
    elif start[0] == end[0]:
        distance = abs(start[1] - end[1]) + 1
        if distance != PIECES[piece]["size"]:
            return {"is_legal": False, "msg": WRONG_SIZE.format(piece_size=PIECES[piece]["size"], distance=distance)}
        else:
            return {"is_legal": True, "msg": LEGAL_PLACEMENT}
    elif start[1] == end[1]:
        distance = abs(start[0] - end[0]) + 1
        if distance != PIECES[piece]["size"]:
            return {"is_legal": False, "msg": WRONG_SIZE.format(piece_size=PIECES[piece]["size"], distance=distance)}
        else:
            return {"is_legal": True, "msg": LEGAL_PLACEMENT}
    else:
        return {"is_legal": False, "msg": UNKNOWN_ERROR}

# VALIDATES IF THE SQUARES WHERE PIECES WISHES TO BE PLACED ARE EMPTY
def validate_board_square(board, piece, start, end):
    for x in range(start[1], end[1] + 1):
        for y in range(start[0], end[0] + 1):
            if board[x][y] != EMPTY_CODE:
                return {"is_legal": False, "msg": BOARD_SQUARE_CONFLICT}

    return {"is_legal": True, "msg": BOARD_SQUARE_CONFLICT}


# CHECKS IF IT IS POSSIBLE TO PLACE A PIECE IN A POSITION
def validate_placement(board, piece, start, end):
    print("Validating placement...")
    is_legal_position = validate_position(piece, start, end)
    print(is_legal_position)
    if is_legal_position.get("is_legal", False):
        is_legal_square = validate_board_square(board, piece, start, end)
        if is_legal_square.get("is_legal", False):
            return {"is_legal": True, "msg": LEGAL_PLACEMENT}
        else:
            return is_legal_square
    else:
        return is_legal_position


# PLACES A PIECE IN THE BOARD
def place_piece(board, piece, start, end):
    is_valid_placement = validate_placement(board, piece, start, end)
    if is_valid_placement["is_legal"]:
        for x in range(start[1], end[1] + 1):
            for y in range(start[0], end[0] + 1):
                board[x][y] = PIECES.get(piece).get("code")
        return {"is_legal": True, "msg": LEGAL_PLACEMENT, "board": board}

    else:
        return {"is_legal": False, "msg": is_valid_placement["msg"], "board": board}


# TRANSLATES THE SLOT CODE INTO A VECTOR
def get_square(slot_code):
    square = [ord(slot_code.split("_")[0]) - ord("A"), int(slot_code.split("_")[1])]
    return square

def get_ship_id(ship):
    ship_id = ship.replace(" ", "_").lower()
    return ship_id


def save_board(user_id, board):
    print("Saving board to DynamoDB")

    table = dynamodb.Table(os.environ[CURRENT_GAMES_TABLE])
    item = {
        'id': user_id,
        'user_board': board,
        'opponent_board': board
    }
    
    response = table.put_item(Item=item)

    return response

