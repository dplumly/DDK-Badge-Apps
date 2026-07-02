import time, math, random, picovector
from picovector import vec2

badge.mode(LORES)
SCREEN_W, SCREEN_H = 40, 26

# ── Modes ─────────────────────────────────────────────────────────────────────
MODE_PSYCH        = 0
MODE_CRT          = 1
MODE_RAIN         = 2
MODE_MATRIX       = 3
MODE_FIRE         = 4
MODE_SMOKE_FADE   = 5
MODE_LASER_ENGRAVE = 6
MODE_PACMAN_EATER = 7 
TOTAL_MODES       = 8

# ── Global State ──────────────────────────────────────────────────────────────
current_mode     = MODE_PSYCH
last_button_time = 0
tick             = 0.0
INPUT_COOLDOWN_MS = 250 

# ── Multi-Name Configuration ──────────────────────────────────────────────────
NAME_OPTIONS     = ["Sarah", "SK"]
current_name_idx = 0

# ── Fonts Engine (The Complete 34-Font Library) ────────────────────────────────
FONTS_LIST = []
FONT_NAMES = [
    "smart", "compass", "nope", "ark", "desert", "torch", "sins", "teatime", 
    "hungry", "kobold", "lookout", "loser", "winds", "match", "corset", "unfair", 
    "saga", "memo", "outflank", "salty", "awesome", "yolk", "vest", "holotype", 
    "yesterday", "absolute", "fear", "troll", "bacteria", "curse", "ziplock", 
    "futile", "manticore", "more", "ignore"
]

# Pull every single verified font asset straight out of the rom_font namespace safely
for name in FONT_NAMES:
    try:
        font_obj = getattr(rom_font, name)
        if font_obj is not None:
            FONTS_LIST.append(font_obj)
    except AttributeError:
        pass

if len(FONTS_LIST) == 0:
    FONTS_LIST = [rom_font.smart, rom_font.compass, rom_font.nope]

current_font_idx = 0

# CRT State
scanline_y       = 0
v_scroll         = 0
glitch_type      = 0
glitch_timer     = 0

# Shared Column State for Rain & Matrix
columns = [[x, random.uniform(-20, 0), random.uniform(0.1, 0.3), random.getrandbits(32)] for x in range(SCREEN_W)]

# Fire Buffer State
fire_buffer = [0] * (SCREEN_W * (SCREEN_H + 1))

# ── Helpers ───────────────────────────────────────────────────────────────────
def draw_snow(density=200, brightness=255):
    for _ in range(density):
        rx, ry = random.randint(0, 39), random.randint(0, 25)
        lum = random.randint(0, brightness)
        screen.pen = color.rgb(lum, lum, lum)
        screen.rectangle(rx, ry, 1, 1)

def update_fire_simulation():
    for x in range(SCREEN_W):
        fire_buffer[(SCREEN_H * SCREEN_W) + x] = random.choice([0, 160, 255, 255, 255])
        
    for y in range(1, SCREEN_H + 1):
        for x in range(SCREEN_W):
            above_idx = ((y - 1) * SCREEN_W) + x
            drift = random.choice([-1, 0, 1])
            source_x = (x + drift) % SCREEN_W
            source_idx = (y * SCREEN_W) + source_x
            
            decay = random.randint(12, 28)
            new_val = fire_buffer[source_idx] - decay
            fire_buffer[above_idx] = max(0, new_val)

def draw_centered_text(text, font, text_color, y_offset=-2):
    screen.font = font
    tw, th = screen.measure_text(text)
    
    start_x = (SCREEN_W - tw) // 2
    start_y = ((SCREEN_H - th) // 2) + y_offset
    screen.pen = text_color
    screen.text(text, start_x, start_y)

# ── Main Update Loop ──────────────────────────────────────────────────────────
def update():
    global current_mode, last_button_time, tick, scanline_y, v_scroll, glitch_type, glitch_timer, current_font_idx, current_name_idx

    now = time.ticks_ms()
    active_font = FONTS_LIST[current_font_idx]
    active_name = NAME_OPTIONS[current_name_idx]
    
    # ── Unified Input Handling ────────────────────────────────────────────────
    if now - last_button_time > INPUT_COOLDOWN_MS:
        changed = False
        
        if badge.pressed(BUTTON_C):
            current_mode = (current_mode + 1) % TOTAL_MODES
            changed = True
        elif badge.pressed(BUTTON_A):
            current_mode = (current_mode - 1) % TOTAL_MODES
            changed = True
        elif badge.pressed(BUTTON_B):  # ── BUTTON B: Cycles the text between Name & Initils
            current_name_idx = (current_name_idx + 1) % len(NAME_OPTIONS)
            changed = True
        elif badge.pressed(BUTTON_UP):
            current_font_idx = (current_font_idx - 1) % len(FONTS_LIST)
            changed = True
        elif badge.pressed(BUTTON_DOWN):
            current_font_idx = (current_font_idx + 1) % len(FONTS_LIST)
            changed = True
            
        if changed:
            last_button_time = now
            tick = 0.0 
            screen.pen = color.rgb(0, 0, 0)
            screen.clear()
            return

    # ── MODE 0: PSYCHEDELIC ───────────────────────────────────────────────────
    if current_mode == MODE_PSYCH:
        screen.pen = color.rgb(10, 5, 25)
        screen.clear()
        screen.alpha = 255
        blob_data = []
        for i in range(5):
            offset = i * 1.4
            cx = (SCREEN_W / 2) + math.sin(tick * 0.6 + offset) * 15
            cy = (SCREEN_H / 2) + math.cos(tick * 0.4 + offset) * 10
            r = int((math.sin(tick * 0.8 + offset) + 1) * 90)
            g = int((math.sin(tick * 0.8 + offset + 2.1) + 1) * 90)
            b = int((math.sin(tick * 0.8 + offset + 4.2) + 1) * 90)
            blob_data.append({'x': int(cx), 'y': int(cy), 'r': r, 'g': g, 'b': b})
        for r_step in range(20, 0, -2):
            fade = (1.0 - (r_step / 22.0)) ** 2
            for b in blob_data:
                if fade > 0.05:
                    screen.pen = color.rgb(int(b['r']*fade), int(b['g']*fade), int(b['b']*fade))
                    screen.circle(b['x'], b['y'], r_step)
        
        glow_val = int(((math.sin(now / 1800.0) + 1.0) * 105) + 45)
        text_faded_color = color.rgb(glow_val, glow_val, glow_val)
        
        screen.alpha = 255
        draw_centered_text(active_name, active_font, text_faded_color, y_offset=-2)
        tick += 0.015

    # ── MODE 1: CRT ───────────────────────────────────────────────────────────
    elif current_mode == MODE_CRT:
        screen.pen = color.rgb(10, 10, 15)
        screen.clear()
        if now > glitch_timer:
            glitch_type = random.randint(0, 4)
            glitch_timer = now + random.randint(500, 3000)
            
        if glitch_type == 0:
            draw_snow(300, 200)
            if random.random() < 0.1: draw_centered_text(active_name, active_font, color.white, y_offset=-2)
        elif glitch_type == 1:
            draw_snow(100, 150)
            v_scroll = (v_scroll + 2) % SCREEN_H
            draw_centered_text(active_name, active_font, color.white, y_offset=-2) 
        elif glitch_type == 2:
            draw_snow(80, 127)
            for s in range(0, SCREEN_H, 4):
                offset = random.randint(-4, 4) if random.random() < 0.3 else 0
                draw_centered_text(active_name, active_font, color.white, y_offset=-2)
        elif glitch_type == 3:
            draw_snow(400, 255)
            if random.random() < 0.2: draw_centered_text(active_name, active_font, color.white, y_offset=-2)
        elif glitch_type == 4:
            draw_centered_text(active_name, active_font, color.white, y_offset=-2)
            draw_snow(50, 100)
            screen.pen = color.rgb(255, 255, 255)
            for _ in range(3):
                screen.rectangle(0, random.randint(0, 25), SCREEN_W, random.randint(1, 3))
        scan_speed = 3 if glitch_type == 4 else 1
        screen.pen = color.rgb(200, 200, 255)
        screen.rectangle(0, scanline_y, SCREEN_W, 1)
        scanline_y = (scanline_y + scan_speed) % SCREEN_H

    # ── MODE 2: RAIN ──────────────────────────────────────────────────────────
    elif current_mode == MODE_RAIN:
        screen.pen = color.rgb(0, 5, 0)
        screen.clear()
        
        screen.alpha = 100
        draw_centered_text(active_name, active_font, color.white, y_offset=-2)
        screen.alpha = 255
        
        for col in columns:
            col[1] += col[2]
            if col[1] > SCREEN_H + 5: col[1] = random.uniform(-10, 0)
            x, y = int(col[0]), int(col[1])
            for t in range(6):
                if 0 <= y - t < SCREEN_H:
                    lum = int(200 * (1.0 - (t / 6.0)))
                    screen.pen = color.rgb(0, lum, 0)
                    screen.rectangle(x, y - t, 1, 1)

    # ── MODE 3: MATRIX ────────────────────────────────────────────────────────
    elif current_mode == MODE_MATRIX:
        screen.pen = color.rgb(0, 5, 0)
        screen.clear()
        
        screen.alpha = 140 if random.random() > 0.05 else 255
        draw_centered_text(active_name, active_font, color.white, y_offset=-2)
        screen.alpha = 255
        
        for x in range(0, SCREEN_W, 2):
            col = columns[x]
            col[0] -= col[2] * 1.5
            if col[0] < 0:
                col[0] = SCREEN_H
                col[3] = random.getrandbits(32)
            for y_idx in range(13):
                y_pos = int(col[0] + (y_idx * 2)) % SCREEN_H
                is_bit_on = (col[3] >> y_idx) & 1
                if is_bit_on:
                    screen.pen = color.rgb(0, 180, 0)
                    if (col[3] >> (y_idx + 13)) & 1:
                        screen.rectangle(x, y_pos, 1, 1)
                    else:
                        screen.rectangle(x, y_pos, 1, 2)

    # ── MODE 4: FIRE & RISING SMOKE ───────────────────────────────────────────
    elif current_mode == MODE_FIRE:
        screen.pen = color.rgb(0, 0, 0)
        screen.clear()
        
        update_fire_simulation()
        draw_centered_text(active_name, active_font, color.white, y_offset=-2)
            
        for y in range(SCREEN_H):
            for x in range(SCREEN_W):
                val = fire_buffer[(y * SCREEN_W) + x]
                if val > 20:  
                    screen.pen = color.rgb(val, val, val)
                    screen.rectangle(x, y, 1, 1)

    # ── MODE 5: ORGANIC SMOKE DISSOLVE ────────────────────────────────────────
    elif current_mode == MODE_SMOKE_FADE:
        screen.pen = color.rgb(0, 0, 0)
        screen.clear()
        
        wave = math.sin(now / 1500.0) * 1.2
        draw_centered_text(active_name, active_font, color.white, y_offset=-2)
        
        for y in range(SCREEN_H):
            for x in range(SCREEN_W):
                noise = math.sin(x * 0.3 + tick) * math.cos(y * 0.4 - tick * 0.5)
                if noise > wave:
                    screen.pen = color.rgb(0, 0, 0)
                    screen.rectangle(x, y, 1, 1)
                        
        tick += 0.04

    # ── MODE 6: LASER ENGRAVER SWEEP ──────────────────────────────────────────
    elif current_mode == MODE_LASER_ENGRAVE:
        screen.pen = color.rgb(0, 0, 0)
        screen.clear()

        laser_x = int((math.sin(tick * 1.2) + 1.0) * 0.5 * (SCREEN_W + 10)) - 5
        draw_centered_text(active_name, active_font, color.white, y_offset=-2)

        for y in range(SCREEN_H):
            for x in range(SCREEN_W):
                dist = x - laser_x
                if dist == 0:
                    screen.pen = color.rgb(255, 255, 255)
                    screen.rectangle(x, y, 1, 1)
                elif 1 <= dist <= 3:
                    if (x + y) % 2 == 0:
                        screen.pen = color.rgb(255, 100, 0) 
                        screen.rectangle(x, y, 1, 1)
                elif dist > 3:
                    screen.pen = color.rgb(0, 0, 0)
                    screen.rectangle(x, y, 1, 1)

        tick += 0.035

    # ── MODE 7: PACMAN PELLET REVEAL ──────────────────────────────────────────
    elif current_mode == MODE_PACMAN_EATER:
        screen.pen = color.rgb(0, 0, 0)
        screen.clear()

        total_steps = (SCREEN_W + 12)
        current_step = int(tick * 0.2) % (total_steps * 3)
        
        chomp_x = (current_step % total_steps) - 6
        chomp_row = current_step // total_steps  
        
        y_lanes = [6, 14, 22]
        pac_y = y_lanes[chomp_row]

        # 1. Render game dots layout
        for y in range(2, SCREEN_H, 4):
            for x in range(2, SCREEN_W, 3):
                row_idx = y_lanes.index(y) if y in y_lanes else -1
                
                has_been_eaten = False
                if row_idx != -1:
                    if row_idx < chomp_row:
                        has_been_eaten = True
                    elif row_idx == chomp_row and x < chomp_x:
                        has_been_eaten = True

                if not has_been_eaten:
                    screen.pen = color.rgb(90, 90, 90) 
                    screen.rectangle(x, y, 1, 1)

        # 2. Permanent Text Layer
        draw_centered_text(active_name, active_font, color.white, y_offset=-2)

        # 3. Render deliberate pixel Pac-Man circle object
        if 0 <= chomp_x < SCREEN_W:
            screen.pen = color.rgb(255, 230, 0) 
            screen.circle(chomp_x, pac_y, 2)
            
            is_mouth_open = (chomp_x % 2 == 0)
            if is_mouth_open:
                screen.pen = color.rgb(0, 0, 0) 
                screen.rectangle(chomp_x, pac_y, 3, 1)
                screen.rectangle(chomp_x + 1, pac_y - 1, 2, 3)

        tick += 0.2

run(update)

