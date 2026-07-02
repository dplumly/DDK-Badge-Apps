import time, os, sys
from picovector import vec2

APP_DIR = "/system/apps/mario"
os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

badge.mode(LORES)

# Splitting your 240x22 image into exactly 12 columns and 1 row
try:
    sprites = SpriteSheet("assets/mario.png", 12, 1)
except:
    sprites = None

# --- CONTROL VARIABLES ---
ANIMATION_DELAY = 8  # Higher = slower running animation loop
current_frame = 0
frame_timer = 0

mario_y = 0.0          # Fits the 22px height nicely on the screen
mario_direction = 0.05
bg_scroll = 0.0

def update():
    global mario_y, mario_direction, bg_scroll, current_frame, frame_timer
    
    screen.pen = color.rgb(0, 0, 0)
    screen.clear()

    # --- 1. ANIMATION TIMING ---
    frame_timer += 1
    if frame_timer >= ANIMATION_DELAY:
        # Loop smoothly through your 12 frames (0 to 11)
        current_frame = (current_frame + 1) % 12
        frame_timer = 0

    # --- 2. MOVE ENVIRONMENT ---
    mario_y += mario_direction
    if mario_y > 1.0 or mario_y < 0.0:
        mario_direction *= -1

    bg_scroll = (bg_scroll - 0.3) % 8.0

    # --- 3. RENDER GRAPHICS ---
    # Thicker road lines (Height changed to 4 to fill the bottom 3 pixels)
    screen.pen = color.rgb(80, 80, 80) 
    for i in range(-1, 7):
        x_pos = int((i * 8) + bg_scroll)
        screen.rectangle(x_pos, 22, 4, 4)

    # Draw Mario
    if sprites:
        frame = sprites.sprite(current_frame, 0)
        # Locked flat at X=2 so he stands completely still while animating
        screen.blit(frame, vec2(2, int(mario_y)))
    
    time.sleep(0.02)

run(update)
