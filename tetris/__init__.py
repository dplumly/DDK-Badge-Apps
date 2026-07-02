import time
import math
import random
import picovector
from picovector import vec2

# ── Hardware Setup ────────────────────────────────────────────────────────────
badge.mode(LORES)
SCREEN_W, SCREEN_H = 40, 26

# ── Tetris Engine Dimensions & Positioning ────────────────────────────────────
TETRIS_W, TETRIS_H = 14, 24
BOARD_X = (SCREEN_W - TETRIS_W) // 2
BOARD_Y = (SCREEN_H - TETRIS_H) // 2

board = [[0 for _ in range(TETRIS_W)] for _ in range(TETRIS_H)]

SHAPES = {
    'I': [(0,0), (-1,0), (1,0), (2,0)],
    'O': [(0,0), (1,0), (0,1), (1,1)],
    'T': [(0,0), (-1,0), (1,0), (0,1)],
    'S': [(0,0), (1,0), (0,1), (-1,1)],
    'Z': [(0,0), (-1,0), (0,1), (1,1)],
    'J': [(0,0), (-1,0), (1,0), (-1,1)],
    'L': [(0,0), (-1,0), (1,0), (1,1)]
}

SHAPE_COLORS = {
    'I': (0, 255, 255), 'O': (255, 255, 0), 'T': (128, 0, 128),
    'S': (0, 255, 0),   'Z': (255, 0, 0),   'J': (0, 0, 255), 'L': (255, 165, 0)
}

# ── New HUD Tracking State ────────────────────────────────────────────────────
lines_cleared = 0
next_piece_type = 'I'

current_piece = None
piece_type = 'I'
piece_x, piece_y = 0, 0
last_drop_time = 0
drop_delay = 140 

def spawn_piece():
    global current_piece, piece_type, piece_x, piece_y, next_piece_type
    
    # Current piece becomes what was previously previewed
    piece_type = next_piece_type
    current_piece = list(SHAPES[piece_type])
    piece_x = TETRIS_W // 2
    piece_y = 0
    
    # Roll the random selection for the next upcoming piece
    next_piece_type = random.choice(list(SHAPES.keys()))
    
    if check_collision(piece_x, piece_y, current_piece):
        reset_game()

def reset_game():
    global board, lines_cleared, next_piece_type
    board = [[0 for _ in range(TETRIS_W)] for _ in range(TETRIS_H)]
    lines_cleared = 0
    next_piece_type = random.choice(list(SHAPES.keys()))
    spawn_piece()

def rotate_piece(shape):
    return [(-y, x) for (x, y) in shape]

def check_collision(nx, ny, shape):
    for px, py in shape:
        tx = nx + px
        ty = ny + py
        if tx < 0 or tx >= TETRIS_W or ty >= TETRIS_H:
            return True
        if ty >= 0 and board[ty][tx] != 0:
            return True
    return False

def lock_piece():
    global board, lines_cleared
    for px, py in current_piece:
        tx = piece_x + px
        ty = piece_y + py
        if 0 <= ty < TETRIS_H and 0 <= tx < TETRIS_W:
            board[ty][tx] = SHAPE_COLORS[piece_type]
    
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = TETRIS_H - len(new_board)
    
    if cleared > 0:
        lines_cleared += cleared
        for _ in range(cleared):
            new_board.insert(0, [0 for _ in range(TETRIS_W)])
        board = new_board
        
    spawn_piece()

reset_game()

def update():
    global current_piece, piece_type, piece_x, piece_y, last_drop_time

    now = time.ticks_ms()
    screen.pen = color.rgb(10, 10, 12)
    screen.clear()

    # AI Processing Logic
    if now - last_drop_time > drop_delay:
        last_drop_time = now
        if random.random() < 0.15:
            rotated = rotate_piece(current_piece)
            if not check_collision(piece_x, piece_y, rotated):
                current_piece = rotated
        if random.random() < 0.30:
            dx = random.choice([-1, 1])
            if not check_collision(piece_x + dx, piece_y, current_piece):
                piece_x += dx

        if not check_collision(piece_x, piece_y + 1, current_piece):
            piece_y += 1
        else:
            lock_piece()

    # 1. Draw Core Game Board Frame
    screen.pen = color.rgb(65, 65, 75)
    screen.rectangle(BOARD_X - 1, BOARD_Y - 1, TETRIS_W + 2, TETRIS_H + 2)
    screen.pen = color.rgb(0, 0, 0)
    screen.rectangle(BOARD_X, BOARD_Y, TETRIS_W, TETRIS_H)

    # 2. Draw Stacked Blocks
    for y in range(TETRIS_H):
        for x in range(TETRIS_W):
            cell_rgb = board[y][x]
            if cell_rgb != 0:
                screen.pen = color.rgb(*cell_rgb)
                screen.rectangle(BOARD_X + x, BOARD_Y + y, 1, 1)

    # 3. Draw Falling Block
    if current_piece:
        r, g, b = SHAPE_COLORS[piece_type]
        screen.pen = color.rgb(r, g, b)
        for px, py in current_piece:
            tx = piece_x + px
            ty = piece_y + py
            if 0 <= ty < TETRIS_H and 0 <= tx < TETRIS_W:
                screen.rectangle(BOARD_X + tx, BOARD_Y + ty, 1, 1)

    # ── 4. RENDER NEW SIDE HUD STUFF ──────────────────────────────────────────
    
   # Drop this in place of step 4 in the update function:
    screen.pen = color.rgb(150, 150, 150)
    # Left side background patterns
    screen.rectangle(2, 4, 3, 3)
    screen.rectangle(5, 12, 4, 2)
    screen.rectangle(1, 19, 2, 4)
    
    # Right side background patterns
    screen.rectangle(34, 6, 4, 2)
    screen.rectangle(35, 15, 3, 3)
    screen.rectangle(33, 20, 2, 4)

run(update)
