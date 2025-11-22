import pyxel

# 画面サイズはそのまま。display_scale は好みで調整してOK
pyxel.init(160, 120, title="Janken Game", fps=30)

# Pyxel のマウスカーソルは非表示（そもそも使わない）
pyxel.mouse(False)

# ===== シーン管理 =====
scene = 0          # 0: TITLE, 1: GAME, 2: HOW TO
menu_idx = 0       # START / HOW TO の選択位置

# ===== メニューの配置 =====
MENU = [
    ("START", 48, 70, 64, 12),
    ("HOW TO", 48, 86, 64, 12),
]

# ===== 共通ヘルパー =====
def draw_centered_text(y, text, col):
    text_w = len(text) * 4
    x = (pyxel.width - text_w) // 2
    pyxel.text(x, y, text, col)

# ↑キー（キーボード or ゲームパッド）
def btnp_up():
    return (
        pyxel.btnp(pyxel.KEY_UP)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
    )

# ↓キー（キーボード or ゲームパッド）
def btnp_down():
    return (
        pyxel.btnp(pyxel.KEY_DOWN)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
    )

# 決定（Enter / Space / A,B,X,Y）
def btnp_ok():
    return (
        pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
    )

# ===== UPDATE =====
def update():
    global scene, menu_idx

    if scene == 0:
        # ===== タイトル =====

        # 選択移動（↑↓）
        if btnp_up():
            menu_idx = (menu_idx - 1) % len(MENU)
        if btnp_down():
            menu_idx = (menu_idx + 1) % len(MENU)

        # 決定（OKボタン）
        if btnp_ok():
            if menu_idx == 0:
                scene = 1
            else:
                scene = 2

    elif scene == 1:
        # ===== ゲーム画面（仮） =====

        # タイトルに戻る
        if btnp_ok():
            scene = 0

    elif scene == 2:
        # ===== HOW TO 画面 =====
        if btnp_ok():
            scene = 0

# ===== DRAW =====
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

            # ▶ カーソル（点滅）
            if hi and pyxel.frame_count % 20 < 10:
                cx = x - 6
                cy1 = y + 2
                cy2 = y + h - 2
                cm = (cy1 + cy2) // 2
                pyxel.tri(cx + 4, cm, cx, cy1, cx, cy2, 7)

        draw_centered_text(110, "ARROW / GAMEPAD + ENTER/A/B/X/Y", 13)

    elif scene == 1:
        # ===== GAME画面（仮） =====
        pyxel.cls(1)
        draw_centered_text(40, "GAME START!", 7)
        draw_centered_text(70, "Janken part is here", 7)
        draw_centered_text(100, "Press ENTER/A/B/X/Y to back", 11)

    elif scene == 2:
        # ===== HOW TO 画面 =====
        pyxel.cls(0)
        draw_centered_text(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Use ARROW or GAMEPAD", 7)
        pyxel.text(10, 60, "- Press ENTER / BUTTONS", 7)
        pyxel.text(10, 80, "Press ENTER / BUTTONS to TITLE", 13)

pyxel.run(update, draw)