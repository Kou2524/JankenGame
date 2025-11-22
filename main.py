import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)
pyxel.mouse(True)

# 0: TITLE / 1: GAME / 2: HOW TO
scene = 0
menu_idx = 0  # 選択中の項目（0: START, 1: HOW TO）

# (表示名, x, y, w, h) ← 枠サイズを統一
MENU = [
    ("START", 48, 70, 64, 12),
    ("HOW TO", 48, 86, 64, 12),
]


def in_rect(mx, my, x, y, w, h):
    return x <= mx < x + w and y <= my < y + h


def draw_centered_text(y, text, col):
    text_w = len(text) * 4
    x = (pyxel.width - text_w) // 2
    pyxel.text(x, y, text, col)


def update():
    global scene, menu_idx

    if scene == 0:
        # ===== タイトル画面 =====
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # ▼ PC版のマウスホバー反応を消す（ここコメントアウトのまま）
        # for i, (_, x, y, w, h) in enumerate(MENU):
        #     if in_rect(mx, my, x, y, w, h):
        #         menu_idx = i

        # ↑↓キーで選択移動（PC用）
        if pyxel.btnp(pyxel.KEY_UP):
            menu_idx = (menu_idx - 1) % len(MENU)
        if pyxel.btnp(pyxel.KEY_DOWN):
            menu_idx = (menu_idx + 1) % len(MENU)

        # SPACE / ENTER で決定（PC用）
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            if menu_idx == 0:
                scene = 1
            elif menu_idx == 1:
                scene = 2

        # クリック / タップで決定（PC / スマホ共通）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # スマホでも押しやすいように、
            # X座標は無視して「Yの位置」だけでどっちのボタンか判定する
            if 70 <= my < 82:  # START 行付近
                menu_idx = 0
                scene = 1
            elif 86 <= my < 98:  # HOW TO 行付近
                menu_idx = 1
                scene = 2

    elif scene == 1:
        # ===== ゲーム画面（仮） =====
        if (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        ):
            scene = 0

    elif scene == 2:
        # ===== HOW TO 画面 =====
        if (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        ):
            scene = 0


def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== タイトル描画 =====
        draw_centered_text(30, "JANKEN GAME", 7)

        # メニュー描画（START / HOW TO）
        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)  # 選択中？

            border_col = 10 if hi else 5  # 黄 or 青
            text_col = 7 if hi else 6      # 白 or 灰

            # 枠線
            pyxel.rectb(x, y, w, h, border_col)

            # ラベル文字
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, text_col)

            # ▶ カーソル（白 / 右向き / 点滅）
            if hi:
                # 点滅（10フレームON、10フレームOFF）
                if pyxel.frame_count % 20 < 10:
                    cx = x - 6         # 枠の左
                    cy1 = y + 2
                    cy2 = y + h - 2
                    cm = (cy1 + cy2) // 2

                    # ▶ の三角形（tipが右側）
                    pyxel.tri(
                        cx + 4, cm,  # 先端（右）
                        cx,     cy1, # 左上
                        cx,     cy2, # 左下
                        7            # 色：白
                    )

        # 説明文
        draw_centered_text(110, "ARROW + ENTER / CLICK", 13)

    elif scene == 1:
        # ===== GAME画面（仮） =====
        pyxel.cls(1)
        draw_centered_text(40, "GAME START!", 7)
        draw_centered_text(70, "Janken part is here", 7)
        draw_centered_text(100, "Press SPACE/CLICK to back", 11)

    elif scene == 2:
        # ===== HOW TO 画面 =====
        pyxel.cls(0)
        draw_centered_text(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Select ROCK / SCISSORS / PAPER", 7)
        pyxel.text(10, 60, "- Win 3 times to clear", 7)
        pyxel.text(10, 80, "Press SPACE/CLICK to TITLE", 13)


pyxel.run(update, draw)