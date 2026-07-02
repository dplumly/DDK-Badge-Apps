import time

badge.mode(LORES)
SCREEN_W, SCREEN_H = 40, 26

# ── DVD State ─────────────────────────────────────────────────────────────────
dvd_x = 10.0
dvd_y = 8.0
dvd_vx = 0.3
dvd_vy = 0.2

# ── Update ────────────────────────────────────────────────────────────────────
def update():
    global dvd_x, dvd_y, dvd_vx, dvd_vy

    time.sleep_ms(50)

    screen.font = rom_font.smart
    tw, th = screen.measure_text("DVD")
    th = max(th, 4)

    dvd_x += dvd_vx
    dvd_y += dvd_vy

    if dvd_x <= 0:
        dvd_x = 0
        dvd_vx = abs(dvd_vx)
    elif dvd_x + tw >= SCREEN_W:
        dvd_x = SCREEN_W - tw
        dvd_vx = -abs(dvd_vx)

    if dvd_y <= 0:
        dvd_y = 0
        dvd_vy = abs(dvd_vy)
    elif dvd_y >= SCREEN_H - th:
        dvd_y = SCREEN_H - th
        dvd_vy = -abs(dvd_vy)

    screen.pen = color.rgb(0, 0, 0)
    screen.clear()
    screen.pen = color.rgb(255, 255, 255)
    screen.text("DVD", int(dvd_x), int(dvd_y))

run(update)
