import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)

# 0: TITLE / 1: GAME
scene = 0

# ボタンを押したあと、何フレーム黄色にするか
press_timer = 0

# (表示名, x, y, w, h)
MENU = [
    ("START", 52, 72, 56, 12),
]


def btn_decide():
    # SPACE / ENTER / クリック（Web版は btnp(0) が左クリック）
    return (
        pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(0)  # ← ここだけが Web版 pyxel.js の正解！
    )


def in_rect(mx, my, x, y, w, h):
    return x <= mx < x + w and y <= my < y + h


def draw_centered_text(y, text, col):
    text_w = len(text) * 4
    x = (pyxel.width - text_w) // 2
    pyxel.text(x, y, text, col)


def update():
    global scene, press_timer

    if scene == 0:
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        label, x, y, w, h = MENU[0]

        if press_timer > 0:
            # 黄色の点滅中
            press_timer -= 1
            if press_timer == 0:
                # 点滅が終わったらゲームへ
                scene = 1

        else:
            # まだ押されていない状態
            if in_rect(mx, my, x, y, w, h) and btn_decide():
                # ボタンの上で押された → 黄色点滅開始
                press_timer = 6  # 6フレーム光らせる

    else:
        # GAME画面：SPACE/ENTER/クリックで戻る（仮）
        if btn_decide():
            scene = 0


def draw():
    pyxel.cls(0)

    if scene == 0:
        # タイトル
        draw_centered_text(45, "JANKEN GAME", 7)

        # START ボタン
        label, x, y, w, h = MENU[0]

        # ★ 黄色点滅中：黄色、それ以外：青
        if press_timer > 0:
            border_col = 10  # 黄色
            text_col = 7
        else:
            border_col = 5   # 青
            text_col = 6

        pyxel.rectb(x, y, w, h, border_col)
        tx = x + (w - len(label) * 4) // 2
        pyxel.text(tx, y + 3, label, text_col)

        # 説明文
        draw_centered_text(110, "Hover and press SPACE/ENTER", 13)

    else:
        # GAME画面
        pyxel.cls(1)
        draw_centered_text(58, "GAME START!", 7)
        draw_centered_text(100, "Press SPACE/ENTER to back", 11)


pyxel.run(update, draw)