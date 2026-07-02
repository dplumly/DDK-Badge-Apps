import time
import math
import random
import picovector
from picovector import vec2

# ── Hardware Setup ────────────────────────────────────────────────────────────
badge.mode(LORES)
SCREEN_W, SCREEN_H = 40, 26

# ── Game State Arrays ─────────────────────────────────────────────────────────
invaders = []       
player_lasers = []  
alien_lasers = []   
bunkers = []        

# ── Timing Gates (Fixed Frame Multipliers) ────────────────────────────────────
last_laser_tick  = 0
last_alien_tick  = 0
last_player_tick = 0

LASER_DELAY   = 40   # Physics updates every 40ms
PLAYER_DELAY  = 50   # Player tank moves every 50ms
BASE_ALIEN_DELAY = 600 # Base alien movement speed (ms)

# ── Position / Movement Globals ───────────────────────────────────────────────
player_x = SCREEN_W // 2 - 1
player_dir = 1
player_last_shoot = 0
alien_dir = 1

game_over_timer = 0
is_game_over = False

def init_game():
    global invaders, player_lasers, alien_lasers, bunkers
    global player_x, player_dir, alien_dir, is_game_over
    global last_laser_tick, last_alien_tick, last_player_tick
    
    now = time.ticks_ms()
    last_laser_tick = now
    last_alien_tick = now
    last_player_tick = now
    
    is_game_over = False
    player_x = SCREEN_W // 2 - 1
    player_dir = 1
    alien_dir = 1
    
    player_lasers = []
    alien_lasers = []
    
    # Spawn Invader Grid (4 columns x 3 rows)
    invaders = []
    for row in range(3):
        for col in range(4):
            invaders.append({
                "x": 4 + col * 6,
                "y": 2 + row * 4,
                "alive": True,
                "type": row
            })
            
    # Spawn 2 Destructible Defensive Bunkers
    bunkers = []
    for bx in range(4):
        for by in range(2):
            bunkers.append({"x": 8 + bx, "y": 18 + by, "health": 3})
    for bx in range(4):
        for by in range(2):
            bunkers.append({"x": 28 + bx, "y": 18 + by, "health": 3})

# Initialize on boot
init_game()

# ── Main Loop ─────────────────────────────────────────────────────────────────
def update():
    global player_x, player_dir, player_last_shoot, alien_dir
    global invaders, player_lasers, alien_lasers, bunkers, is_game_over, game_over_timer
    global last_laser_tick, last_alien_tick, last_player_tick

    now = time.ticks_ms()

    # ── HANDLE GAME OVER RESET (Prevents aggressive flashing) ────────────────
    if is_game_over:
        screen.pen = color.rgb(40, 0, 0)
        screen.clear()
        # Draw a tiny sad face indicator or pixel block so you know it's resetting
        screen.pen = color.rgb(255, 255, 255)
        screen.rectangle(SCREEN_W//2 - 1, SCREEN_H//2 - 1, 2, 2)
        if now > game_over_timer:
            init_game()
        return

    # Count surviving invaders
    alive_count = sum(1 for inv in invaders if inv["alive"])
    if alive_count == 0:
        is_game_over = True
        game_over_timer = now + 2000 # Wait 2 seconds before restart
        return

    # ── 1. FIXED TICK: PLAYER MOVEMENT & SHOOTING ────────────────────────────
    if now - last_player_tick > PLAYER_DELAY:
        last_player_tick = now
        player_x += player_dir
        if player_x <= 0:
            player_x = 0
            player_dir = 1
        elif player_x >= SCREEN_W - 3:
            player_x = SCREEN_W - 3
            player_dir = -1

        # Periodic firing behavior tied to player ticks
        if now - player_last_shoot > 700:
            player_last_shoot = now
            player_lasers.append({"x": player_x + 1, "y": 21})

    # ── 2. FIXED TICK: ALIEN MOVEMENT (Speeds up as they die) ────────────────
    current_alien_delay = max(70, BASE_ALIEN_DELAY - (12 - alive_count) * 45)
    if now - last_alien_tick > current_alien_delay:
        last_alien_tick = now
        
        shift_down = False
        for inv in invaders:
            if inv["alive"]:
                if alien_dir == 1 and inv["x"] >= SCREEN_W - 4:
                    shift_down = True
                    alien_dir = -1
                    break
                elif alien_dir == -1 and inv["x"] <= 1:
                    shift_down = True
                    alien_dir = 1
                    break

        for inv in invaders:
            if inv["alive"]:
                if shift_down:
                    inv["y"] += 1
                    if inv["y"] >= 18: # Reached bunker line
                        is_game_over = True
                        game_over_timer = now + 2000
                else:
                    inv["x"] += alien_dir

        # Randomly select a front-row alien to fire back
        if random.random() < 0.35 and alive_count > 0:
            living_aliens = [inv for inv in invaders if inv["alive"]]
            shooter = random.choice(living_aliens)
            alien_lasers.append({"x": shooter["x"] + 1, "y": shooter["y"] + 2})

    # ── 3. FIXED TICK: LASER PHYSICS & COLLISIONS ────────────────────────────
    if now - last_laser_tick > LASER_DELAY:
        last_laser_tick = now

        # Update Player Lasers (UP)
        for laser in player_lasers[:]:
            laser["y"] -= 1
            lx, ly = laser["x"], laser["y"]

            if ly < 0:
                player_lasers.remove(laser)
                continue

            # Check Alien Hits
            hit = False
            for inv in invaders:
                if inv["alive"]:
                    if inv["x"] <= lx < inv["x"] + 3 and inv["y"] <= ly < inv["y"] + 2:
                        inv["alive"] = False
                        hit = True
                        break
            if hit:
                player_lasers.remove(laser)
                continue

            # Check Bunker Hits
            for b in bunkers:
                if b["health"] > 0 and b["x"] == lx and b["y"] == ly:
                    b["health"] -= 1
                    player_lasers.remove(laser)
                    break

        # Update Alien Lasers (DOWN)
        for laser in alien_lasers[:]:
            laser["y"] += 1
            lx, ly = laser["x"], laser["y"]

            if ly >= SCREEN_H:
                alien_lasers.remove(laser)
                continue

            # Check Bunker Hits
            hit = False
            for b in bunkers:
                if b["health"] > 0 and b["x"] == lx and b["y"] == ly:
                    b["health"] -= 1
                    hit = True
                    break
            if hit:
                alien_lasers.remove(laser)
                continue

            # Check Player Hit
            if 22 <= ly <= 23 and player_x <= lx < player_x + 3:
                is_game_over = True
                game_over_timer = now + 2000

    # ── 4. RENDERING (Runs at screen max refresh rate) ────────────────────────
    screen.pen = color.rgb(5, 5, 10)
    screen.clear()

    # Draw Bunkers
    for b in bunkers:
        if b["health"] > 0:
            if b["health"] == 3: screen.pen = color.rgb(0, 180, 255)
            elif b["health"] == 2: screen.pen = color.rgb(210, 140, 0)
            else: screen.pen = color.rgb(200, 50, 0)
            screen.rectangle(b["x"], b["y"], 1, 1)

    # Draw Player Cannon
    screen.pen = color.rgb(0, 255, 60)
    screen.rectangle(player_x, 23, 3, 1)      
    screen.rectangle(player_x + 1, 22, 1, 1)  

    # Draw Active Invaders
    for inv in invaders:
        if inv["alive"]:
            if inv["type"] == 0: screen.pen = color.rgb(255, 40, 40)
            elif inv["type"] == 1: screen.pen = color.rgb(255, 0, 220)
            else: screen.pen = color.rgb(0, 230, 255)
            
            screen.rectangle(inv["x"], inv["y"], 3, 2)
            # Eyes
            screen.pen = color.rgb(5, 5, 10)
            screen.rectangle(inv["x"] + 1, inv["y"] + 1, 1, 1) 

    # Draw Player Lasers
    screen.pen = color.rgb(255, 255, 0)
    for laser in player_lasers:
        screen.rectangle(laser["x"], laser["y"], 1, 1)

    # Draw Enemy Lasers
    screen.pen = color.rgb(255, 50, 50)
    for laser in alien_lasers:
        screen.rectangle(laser["x"], laser["y"], 1, 1)

run(update)
