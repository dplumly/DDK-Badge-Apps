import time, os, sys, math, random
import urequests
import network

APP_DIR = "/system/apps/weather"
os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

NODE_IP  = "192.168.0.98"
SSID     = "BuzzAxeRampage"
PASSWORD = "The2dude"

badge.mode(LORES)
SCREEN_W, SCREEN_H = 40, 26

temp_str = "---"
hum_str  = "---"
last_fetch   = -60000
data_age     = 0
MAX_AGE_MS   = 90000

# Framerate control (Target: 30 FPS -> ~33ms per frame)
FPS_TARGET = 30
FRAME_MS = int(1000 / FPS_TARGET)
last_frame_time = time.ticks_ms()

# Animation state
current_mode     = 0
TOTAL_MODES      = 5
last_button_time = 0
INPUT_COOLDOWN   = 250
tick             = 0.0

# Particles (for floating particles mode)
particles = [[random.randint(0, 39), random.uniform(0, 25), random.uniform(0.05, 0.2)] for _ in range(20)]

# Dew drops
drops = [[random.randint(0, 39), random.uniform(0, 25), random.uniform(0.1, 0.4), random.randint(80, 200)] for _ in range(15)]

# Aurora bands
aurora_bands = [[random.uniform(0, 25), random.uniform(0.01, 0.03), random.randint(60, 120)] for _ in range(4)]

# WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to WiFi...")
    wlan.connect(SSID, PASSWORD)
    attempts = 0
    while not wlan.isconnected() and attempts < 20:
        time.sleep(0.5)
        attempts += 1

if wlan.isconnected():
    print("WiFi connected:", wlan.ifconfig()[0])
else:
    print("WiFi FAILED")

def draw_weather_text(brightness=255):
    screen.font = rom_font.smart
    screen.pen = color.rgb(brightness, brightness, brightness)
    if time.ticks_diff(time.ticks_ms(), data_age) > MAX_AGE_MS:
        screen.pen = color.rgb(brightness, 0, 0)
        screen.text("NO", 2, -2)
        screen.text("DATA", 2, 8)
    else:
        screen.text(temp_str, 2, -2)
        screen.text(hum_str,  2, 8)

def draw_breathing():
    # Slow pulse of text brightness
    glow = int(((math.sin(tick * 0.8) + 1.0) * 0.5) * 200 + 55)
    screen.pen = color.rgb(0, 0, 0)
    screen.clear()
    draw_weather_text(glow)

def draw_particles():
    screen.pen = color.rgb(0, 0, 0)
    screen.clear()
    for p in particles:
        p[1] -= p[2]
        if p[1] < -1:
            p[1] = SCREEN_H
            p[0] = random.randint(0, 39)
        lum = random.randint(60, 160)
        screen.pen = color.rgb(lum, lum, lum)
        screen.rectangle(int(p[0]), int(p[1]), 1, 1)
    draw_weather_text()

def draw_shimmer():
    screen.pen = color.rgb(0, 0, 0)
    screen.clear()
    # Subtle ripple lines
    for y in range(SCREEN_H):
        wave = math.sin(y * 0.5 + tick * 2.0)
        if wave > 0.7:
            lum = int((wave - 0.7) * 200)
            screen.pen = color.rgb(lum, lum, lum)
            screen.rectangle(0, y, SCREEN_W, 1)
    draw_weather_text()

def draw_aurora():
    screen.pen = color.rgb(0, 0, 0)
    screen.clear()
    for band in aurora_bands:
        band[0] += band[1]
        if band[0] > SCREEN_H + 5:
            band[0] = -3
        y = int(band[0])
        lum = band[2]
        for dy in range(3):
            ry = y + dy
            if 0 <= ry < SCREEN_H:
                fade = int(lum * (1.0 - dy / 3.0))
                screen.pen = color.rgb(fade, fade, fade)
                screen.rectangle(0, ry, SCREEN_W, 1)
    draw_weather_text()

def draw_drops():
    screen.pen = color.rgb(0, 0, 0)
    screen.clear()
    for d in drops:
        d[1] += d[2]
        d[3] = max(0, d[3] - 1)
        if d[1] > SCREEN_H or d[3] == 0:
            d[0] = random.randint(0, 39)
            d[1] = 0
            d[2] = random.uniform(0.1, 0.4)
            d[3] = random.randint(80, 200)
        lum = int((d[3] / 200.0) * 255)
        screen.pen = color.rgb(lum, lum, lum)
        screen.rectangle(int(d[0]), int(d[1]), 1, 2)
    draw_weather_text()

def update():
    global temp_str, hum_str, last_fetch, data_age
    global current_mode, last_button_time, tick, last_frame_time

    now = time.ticks_ms()

    # Frame Rate Regulation
    elapsed = time.ticks_diff(now, last_frame_time)
    if elapsed < FRAME_MS:
        time.sleep_ms(FRAME_MS - elapsed)
        now = time.ticks_ms() # Update 'now' after sleeping
    last_frame_time = now

    # Button B cycles modes
    if time.ticks_diff(now, last_button_time) > INPUT_COOLDOWN:
        if badge.pressed(BUTTON_B):
            current_mode = (current_mode + 1) % TOTAL_MODES
            last_button_time = now
            tick = 0.0

    # Fetch weather
    if time.ticks_diff(now, last_fetch) > 15000:
        if wlan.isconnected():
            try:
                r = urequests.get("http://" + NODE_IP + "/weather", timeout=6)
                data = r.json()
                r.close()
                temp_str = str(data["temp"]) + "F"
                hum_str  = str(data["hum"]) + "%"
                data_age = now
                print("Updated:", temp_str, hum_str)
            except Exception as e:
                print("Fetch error:", e)
        last_fetch = now

    # Draw current mode
    if current_mode == 0:
        draw_breathing()
    elif current_mode == 1:
        draw_particles()
    elif current_mode == 2:
        draw_shimmer()
    elif current_mode == 3:
        draw_aurora()
    elif current_mode == 4:
        draw_drops()

    tick += 0.03

run(update)