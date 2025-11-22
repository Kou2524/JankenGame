import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)
pyxel.mouse(False)

# 0: TITLE / 1: GAME / 2: HOW TO
scene = 0
menu_idx = 0  # 0: START, 1: HOW TO

# (表示名, x, y, w, h)
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 48, 86, 64, 12),
]

def draw_centered_text(y, text, col):
    text_w = len(text) * 4
    pyxel.text((160 - text_w) // 2, y, text, col)

def update():
    global scene, menu_idx

    # タイトル画面
    if scene == 0:
        # 上下で選択移動
        if pyxel.btnp(pyxel.KEY_UP):
            menu_idx = (menu_idx - 1) % 2
        if pyxel.btnp(pyxel.KEY_DOWN):
            menu_idx = (menu_idx + 1) % 2

        # ENTERで決定
        if pyxel.btnp(pyxel.KEY_RETURN):
            if menu_idx == 0:
                scene = 1  # GAMEへ
            else:
                scene = 2  # HOW TOへ

    # HOW TO画面 → ENTERでタイトルへ戻る
    elif scene == 2:
        if pyxel.btnp(pyxel.KEY_RETURN):
            scene = 0

def draw():
    pyxel.cls(0)

    # タイトル画面
    if scene == 0:
        draw_centered_text(30, "JANKEN GAME", 7)

        # START
        pyxel.rectb(MENU[0][1], MENU[0][2], MENU[0][3], MENU[0][4], 10)
        draw_centered_text(MENU[0][2] + 4, "START", 7)

        # HOW TO
        pyxel.rectb(MENU[1][1], MENU[1][2], MENU[1][3], MENU[1][4], 5)
        draw_centered_text(MENU[1][2] + 4, "HOW TO", 7)

        # ▶ 点滅（白）
        blink = (pyxel.frame_count // 10) % 2 == 0
        if blink:
            if menu_idx == 0:
                pyxel.text(MENU[0][1] - 10, MENU[0][2] + 4, "▶", 7)
            else:
                pyxel.text(MENU[1][1] - 10, MENU[1][2] + 4, "▶", 7)

        pyxel.text(30, 110, "ARROW + ENTER", 7)

    # GAME画面
    elif scene == 1:
        draw_centered_text(60, "GAME START!", 7)

    # HOW TO画面
    elif scene == 2:
        draw_centered_text(40, "HOW TO PLAY", 7)
        draw_centered_text(100, "ENTER TO BACK", 7)

pyxel.run(update, draw)