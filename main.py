import pyxel

# ===== JS 側の set_bgm_scene を呼べるようにする =====
try:
    from js import set_bgm_scene as _set_bgm_scene_js

    def set_bgm_scene(scene: int) -> None:
        _set_bgm_scene_js(scene)

except ImportError:
    # ローカル実行(Pythonistaとか)用のダミー
    def set_bgm_scene(scene: int) -> None:
        pass


pyxel.init(160, 120, title="Janken Game", fps=30)
pyxel.mouse(False)

# 0: TITLE, 1: GAME, 2: HOW TO
scene = 0
menu_idx = 0

MENU = [
    ("START", 48, 70, 64, 12),
    ("HOW TO", 48, 86, 64, 12),
]


def draw_centered_text(y, text, col):
    text_w = len(text) * 4
    x = (pyxel.width - text_w) // 2
    pyxel.text(x, y, text, col)


def btnp_up():
    return (
        pyxel.btnp(pyxel.KEY_UP)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
    )


def btnp_down():
    return (
        pyxel.btnp(pyxel.KEY_DOWN)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
    )


def btnp_ok():
    return (
        pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
    )


def update():
    global scene, menu_idx

    old_scene = scene  # シーン変更検知用

    if scene == 0:
        # ===== TITLE =====

        # 上：一番上ならそれ以上行かない
        if btnp_up():
            if menu_idx > 0:
                menu_idx -= 1

        # 下：一番下ならそれ以上行かない
        if btnp_down():
            if menu_idx < len(MENU) - 1:
                menu_idx += 1

        # 決定
        if btnp_ok():
            if menu_idx == 0:
                scene = 1  # GAME
            else:
                scene = 2  # HOW TO

    elif scene == 1:
        # ===== GAME =====
        if btnp_ok():
            scene = 0  # タイトルに戻る

    elif scene == 2:
        # ===== HOW TO =====
        if btnp_ok():
            scene = 0  # タイトルに戻る

    # シーンが変わったときだけ JS 側に通知
    if scene != old_scene:
        set_bgm_scene(scene)


def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== TITLE =====
        draw_centered_text(30, "JANKEN GAME", 7)

        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)
            border_col = 10 if hi else 5
            text_col = 7 if hi else 6

            pyxel.rectb(x, y, w, h, border_col)
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, text_col)

            # ▶ カーソル（点滅）
            if hi and pyxel.frame_count % 20 < 10:
                cx = x - 6
                cy1 = y + 2
                cy2 = y + h - 2
                cm = (cy1 + cy2) // 2
                pyxel.tri(cx + 4, cm, cx, cy1, cx, cy2, 7)

        # 下の行はタイトル画面下部に文字を表示するコード
        # draw_centered_text(110, "ARROW / GAMEPAD + ENTER/A/B/X/Y", 13)

    elif scene == 1:
        # ===== GAME（中身はあとで作る） =====
        pyxel.cls(1)
        draw_centered_text(40, "GAME SCREEN", 7)
        draw_centered_text(100, "Press ENTER / BUTTONS to TITLE", 11)

    elif scene == 2:
        # ===== HOW TO =====
        draw_centered_text(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Use ARROW or GAMEPAD", 7)
        pyxel.text(10, 60, "- Press ENTER / BUTTONS", 7)
        pyxel.text(10, 80, "Press ENTER / BUTTONS to TITLE", 13)


# 最初のシーンも一応通知しておく
set_bgm_scene(scene)

pyxel.run(update, draw)
