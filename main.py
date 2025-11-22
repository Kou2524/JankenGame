import pyxel

# ここで画面を4倍に拡大して表示する！
pyxel.init(
    160,
    120,
    title="Janken Game",
    fps=30,
    display_scale=4,      # ← これが効くやつ！
)

# Pyxel の青いマウスカーソルは非表示
pyxel.mouse(False)

# シーン管理
scene = 0   # 0: TITLE, 1: GAME, 2: HOW TO
menu_idx = 0  # 選択中の項目（0: START, 1: HOW TO）

# メニュー（枠サイズは統一）
MENU = [
    ("START", 48, 70, 64, 12),
    ("HOW TO", 48, 86, 64, 12),
]


def draw_centered_text(y, text, col):
    text_w = len(text) * 4
    x = (pyxel.width - text_w) // 2
    pyxel.text(x, y, text, col)


def update():
    global scene, menu_idx

    if scene == 0:
        # ===== タイトル画面 =====
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # ↑↓キーで選択
        if pyxel.btnp(pyxel.KEY_UP):
            menu_idx = (menu_idx - 1) % len(MENU)
        if pyxel.btnp(pyxel.KEY_DOWN):
            menu_idx = (menu_idx + 1) % len(MENU)

        # SPACE / ENTER で決定
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            if menu_idx == 0:
                scene = 1
            else:
                scene = 2

        # クリック / タップで決定（Y座標だけでざっくり判定）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if 70 <= my < 82:     # START 行
                menu_idx = 0
                scene = 1
            elif 86 <= my < 98:   # HOW TO 行
                menu_idx = 1
                scene = 2

    elif scene == 1:
        # ===== GAME画面 =====
        if (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        ):
            scene = 0

    elif scene == 2:
        # ===== HOW TO画面 =====
        if (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        ):
            scene = 0


def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== タイトル画面 =====
        draw_centered_text(30, "JANKEN GAME", 7)

        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)

            border_col = 10 if hi else 5
            text_col = 7 if hi else 6

            # 枠
            pyxel.rectb(x, y, w, h, border_col)

            # ラベル
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, text_col)

            # ▶（選択中だけ・点滅）
            if hi and pyxel.frame_count % 20 < 10:
                cx = x - 6
                cy1 = y + 2
                cy2 = y + h - 2
                cm = (cy1 + cy2) // 2
                pyxel.tri(
                    cx + 4, cm,  # 先端（右向き）
                    cx,     cy1,
                    cx,     cy2,
                    7,           # 白
                )

        draw_centered_text(110, "ARROW + ENTER / CLICK", 13)

    elif scene == 1:
        pyxel.cls(1)
        draw_centered_text(40, "GAME START!", 7)
        draw_centered_text(70, "Janken part is here", 7)
        draw_centered_text(100, "Press SPACE/CLICK to back", 11)

    elif scene == 2:
        pyxel.cls(0)
        draw_centered_text(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Select ROCK / SCISSORS / PAPER", 7)
        pyxel.text(10, 60, "- Win 3 times to clear", 7)
        pyxel.text(10, 80, "Press SPACE/CLICK to TITLE", 13)


pyxel.run(update, draw)