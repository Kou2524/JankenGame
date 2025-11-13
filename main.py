import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)

# 0: TITLE / 1: GAME / 2: HOW TO
scene = 0
menu_idx = 0  # 選択中の項目（0: START, 1: HOW TO）

# (表示名, x, y, w, h)
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 48, 86, 64, 12),
]


def btn_decide():
    # SPACE / ENTER / 左クリック(0) で決定
    return (
        pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(0)
    )


def in_rect(mx, my, x, y, w, h):
    return x <= mx < x + w and y <= my < y + h


# 横方向の中央にテキストを出す関数
def draw_centered_text(y, text, col):
    text_w = len(text) * 4          # フォント幅4px × 文字数
    x = (pyxel.width - text_w) // 2 # 画面幅から逆算して中央
    pyxel.text(x, y, text, col)


def update():
    global scene, menu_idx

    if scene == 0:
        # ===== タイトル画面 =====
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # マウス位置でホバー反映
        for i, (_, x, y, w, h) in enumerate(MENU):
            if in_rect(mx, my, x, y, w, h):
                menu_idx = i

        # ↑↓キーで移動
        if pyxel.btnp(pyxel.KEY_UP):
            menu_idx = (menu_idx - 1) % len(MENU)
        if pyxel.btnp(pyxel.KEY_DOWN):
            menu_idx = (menu_idx + 1) % len(MENU)

        # 決定
        if btn_decide():
            if menu_idx == 0:
                scene = 1  # START → ゲーム画面
            elif menu_idx == 1:
                scene = 2  # HOW TO → 説明画面

    elif scene == 1:
        # ===== ゲーム画面（仮） =====
        # SPACE / ENTER / クリックでタイトルへ戻る
        if btn_decide():
            scene = 0

    elif scene == 2:
        # ===== HOW TO 画面 =====
        # SPACE / ENTER / クリックでタイトルへ戻る
        if btn_decide():
            scene = 0


def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== タイトル画面描画 =====
        draw_centered_text(45, "JANKEN GAME", 7)

        # メニュー
        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)            # 選択中かどうか
            border_col = 10 if hi else 5    # 選択中:黄 / 非選択:青
            text_col = 7 if hi else 6

            pyxel.rectb(x, y, w, h, border_col)
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, text_col)

        # 説明文
        draw_centered_text(110, "Hover and press SPACE/ENTER", 13)

    elif scene == 1:
        # ===== GAME画面（仮） =====
        pyxel.cls(1)
        draw_centered_text(40, "GAME START!", 7)
        draw_centered_text(70, "Janken part is here", 7)
        draw_centered_text(100, "Press SPACE/ENTER to back", 11)

    elif scene == 2:
        # ===== HOW TO 画面 =====
        pyxel.cls(0)
        draw_centered_text(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Select ROCK / SCISSORS / PAPER", 7)
        pyxel.text(10, 60, "- Win 3 times to clear", 7)
        pyxel.text(10, 80, "Press SPACE/ENTER or click to TITLE", 13)


pyxel.run(update, draw)