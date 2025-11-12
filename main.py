import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)
pyxel.mouse(False)  # ← Pyxel側の十字は出さない

scene = 0
menu_idx = 0

MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 48, 86, 64, 12),
]

def tap_pressed():
    return pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_Z)

def is_hover(mx, my, x, y, w, h):
    return (x <= mx < x + w) and (y <= my < y + h)

def update_title():
    global scene, menu_idx
    mx, my = pyxel.mouse_x, pyxel.mouse_y

    # マウス位置でハイライト
    for i, (_, x, y, w, h) in enumerate(MENU):
        if is_hover(mx, my, x, y, w, h):
            menu_idx = i

    # ↑↓キーでも選択移動
    if pyxel.btnp(pyxel.KEY_UP):
        menu_idx = (menu_idx - 1) % len(MENU)
    if pyxel.btnp(pyxel.KEY_DOWN):
        menu_idx = (menu_idx + 1) % len(MENU)

    # 決定
    if tap_pressed():
        if menu_idx == 0:
            scene = 1
        else:
            pass  # HOW TO は今は未実装

def update_game():
    global scene
    if tap_pressed():
        scene = 0

def update():
    if scene == 0:
        update_title()
    else:
        update_game()

def draw_title():
    pyxel.cls(0)
    pyxel.text(40, 45, "JANKEN GAME", 7)
    for i, (label, x, y, w, h) in enumerate(MENU):
        hover = (i == menu_idx)
        col = 10 if hover else 5
        pyxel.rectb(x, y, w, h, col)
        tx = x + (w - len(label) * 4) // 2
        ty = y + 3
        pyxel.text(tx, ty, label, 7 if hover else 6)
    pyxel.text(18, 110, "Hover and press SPACE/ENTER", 13)

def draw_game():
    pyxel.cls(1)
    pyxel.text(50, 58, "GAME START!", 7)
    pyxel.text(22, 100, "Press SPACE/ENTER to back", 11)

def draw():
    if scene == 0:
        draw_title()
    else:
        draw_game()

pyxel.run(update, draw)