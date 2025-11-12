import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)

# 0: TITLE / 1: GAME
scene = 0
menu_idx = 0  # 選択中の項目

# (表示名, x, y, w, h)
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 48, 86, 64, 12),
]

def btn_decide():
    return pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN)

def in_rect(mx, my, x, y, w, h):
    return x <= mx < x + w and y <= my < y + h

def update():
    global scene, menu_idx

    if scene == 0:
        # マウス位置でホバー反映
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        for i, (_, x, y, w, h) in enumerate(MENU):
            if in_rect(mx, my, x, y, w, h):
                menu_idx = i

        # ↑↓で移動
        if pyxel.btnp(pyxel.KEY_UP):
            menu_idx = (menu_idx - 1) % len(MENU)
        if pyxel.btnp(pyxel.KEY_DOWN):
            menu_idx = (menu_idx + 1) % len(MENU)

        # 決定
        if btn_decide():
            scene = 1 if menu_idx == 0 else 0  # HOW TO は未実装なので据え置き

    else:
        # ゲーム中は決定キーでタイトルへ戻る（仮）
        if btn_decide():
            scene = 0

def draw():
    pyxel.cls(0)

    if scene == 0:
        pyxel.text(40, 45, "JANKEN GAME", 7)

        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)
            pyxel.rectb(x, y, w, h, 10 if hi else 5)
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, 7 if hi else 6)

        pyxel.text(18, 110, "Hover and press SPACE/ENTER", 13)

    else:
        pyxel.cls(1)
        pyxel.text(50, 58, "GAME START!", 7)
        pyxel.text(22, 100, "Press SPACE/ENTER to back", 11)

pyxel.run(update, draw)