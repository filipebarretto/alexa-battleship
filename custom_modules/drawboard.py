from PIL import Image, ImageFont, ImageDraw
import io
import math


from custom_modules import data, dbcontroller
SQUARE_SIZE = 64
SQUARE_PADDING = 8
FONT_SIZE = 32

FONT = ImageFont.truetype("/var/task/src/fonts/OpenSans.ttf", FONT_SIZE)

SQUARE_COLOR_A = (0, 100, 100)
SQUARE_COLOR_B = (0, 120, 120)

HIT_COLOR = (255, 0, 0)
MISS_COLOR = (255, 255, 255)
LETTER_COLOR = (255, 255, 255)
BOARD_BACKGROUND_COLOR = (0, 0, 0)

SHIP_COLOR = (128, 128, 128)

BOARD_WIDTH = 12
BOARD_HEIGHT = 12

def draw_board_without_ships(user_id, board, player):
    board_img = Image.new("RGB", (BOARD_WIDTH, BOARD_HEIGHT), BOARD_BACKGROUND_COLOR)
    board_pixels = board_img.load()
    for x in range(BOARD_WIDTH - 1):
        for y in range(BOARD_HEIGHT - 1):
            if x != 0 and y != 0:
                board_pixels[y, x] = MISS_COLOR if board[x - 1][y - 1] == data.MISS_CODE else (HIT_COLOR if board[x - 1][y - 1] % 10 == data.HIT_CODE else (SQUARE_COLOR_B if (x + y) % 2 else SQUARE_COLOR_A))

    board_img = board_img.resize((BOARD_WIDTH * SQUARE_SIZE, BOARD_HEIGHT * SQUARE_SIZE), Image.NEAREST)
    draw = ImageDraw.Draw(board_img)

    for x in range(BOARD_WIDTH - 1):
        for y in range(BOARD_HEIGHT - 1):
            if x == 0 and y != 0:
                w, h = draw.textsize(data.COLUMNS[y - 1])
                draw.text(((y + 0.5) * SQUARE_SIZE - w, SQUARE_SIZE / 2 - h), data.COLUMNS[y - 1], LETTER_COLOR, font=FONT)
            elif x != 0 and y == 0:
                w, h = draw.textsize(data.ROWS[x - 1])
                draw.text((SQUARE_SIZE / 2 - w, x * SQUARE_SIZE + h / 2), data.ROWS[x - 1], LETTER_COLOR, font=FONT)
    
    in_mem_file = io.BytesIO()
    board_img.save(in_mem_file, format="PNG")
    dbcontroller.save_board_img(user_id, player, in_mem_file.getvalue())


def draw_board_with_ships(user_id, board, player):
    board_img = Image.new("RGB", (BOARD_WIDTH, BOARD_HEIGHT), BOARD_BACKGROUND_COLOR)
    board_pixels = board_img.load()
    draw = ImageDraw.Draw(board_img)
    for x in range(BOARD_WIDTH - 1):
        for y in range(BOARD_HEIGHT - 1):
            if x != 0 and y != 0:
                board_pixels[y, x] = MISS_COLOR if board[x - 1][y - 1] == data.MISS_CODE else (HIT_COLOR if board[x - 1][y - 1] % 10 == data.HIT_CODE else (SHIP_COLOR if board[x - 1][y - 1] > 100 else (SQUARE_COLOR_B if (x + y) % 2 else SQUARE_COLOR_A)))

    board_img = board_img.resize((BOARD_WIDTH * SQUARE_SIZE, BOARD_HEIGHT * SQUARE_SIZE), Image.NEAREST)
    draw = ImageDraw.Draw(board_img)
    
    for x in range(BOARD_WIDTH - 1):
        for y in range(BOARD_HEIGHT - 1):
            if x == 0 and y != 0:
                w, h = draw.textsize(data.COLUMNS[y - 1])
                draw.text(((y + 0.5) * SQUARE_SIZE - w, SQUARE_SIZE / 2 - h), data.COLUMNS[y - 1], LETTER_COLOR, font=FONT)
            elif x != 0 and y == 0:
                w, h = draw.textsize(data.ROWS[x - 1])
                draw.text((SQUARE_SIZE / 2 - w, x * SQUARE_SIZE + h / 2), data.ROWS[x - 1], LETTER_COLOR, font=FONT)

    in_mem_file = io.BytesIO()
    board_img.save(in_mem_file, format="PNG")
    rsp = dbcontroller.save_board_img(user_id, player, in_mem_file.getvalue())

    return rsp

