import pyxel

# ===== JS 側の set_bgm_scene を呼べるようにする =====
try:
    from js import set_bgm_scene as _set_bgm_scene_js

    def set_bgm_scene(scene: int) -> None:
        _set_bgm_scene_js(scene)

except ImportError:
    # ローカル実行用のダミー
    def set_bgm_scene(scene: int) -> None:
        pass


# 画面サイズ
SCREEN_W = 160
SCREEN_H = 120

pyxel.init(SCREEN_W, SCREEN_H, title="Janken Game", fps=30)
pyxel.mouse(False)

# 0: TITLE, 1: GAME, 2: HOW TO
scene = 0
last_scene = -1  # 直前のシーン（BGM切り替え用）

# タイトルメニュー
menu_idx = 0
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 52, 86, 56, 12),
]

# ===== ゲーム状態 =====
game_phase = 0
phase_timer = 0

player_hand = 0
cpu_hand = 0
result = 0
result_decided = False

hand_cursor = 0
continue_cursor = 0

win_streak = 0
show_win_streak = False

HAND_LABELS = ["ROCK", "SCISSORS", "PAPER"]


# ------------------------------
# ヘルパー
# ------------------------------
def draw_centered_text_panel(panel_x, panel_w, y, text, col):
    text_w = len(text) * 4
    x = panel_x + (panel_w - text_w) // 2
    pyxel.text(x, y, text, col)


def is_ok_pressed():
    return (
        pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
    )


def is_left_pressed():
    return pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)


def is_right_pressed():
    return pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)


def reset_game():
    global game_phase, phase_timer, player_hand, cpu_hand
    global result, hand_cursor, continue_cursor, result_decided
    global show_win_streak

    game_phase = 0
    phase_timer = 0
    player_hand = 0
    cpu_hand = 0
    result = 0
    hand_cursor = 0
    continue_cursor = 0
    result_decided = False
    show_win_streak = False


def draw_next_indicator(panel_x, panel_y, panel_w):
    if pyxel.frame_count % 30 < 15:
        cx = panel_x + panel_w - 8
        top_y = panel_y + 22
        pyxel.tri(cx - 2, top_y, cx + 2, top_y, cx, top_y + 4, 7)


# ------------------------------
# UPDATE
# ------------------------------
def update():
    global scene, last_scene, menu_idx
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, continue_cursor, result_decided, win_streak, show_win_streak

    # BGM切り替え
    if scene != last_scene:
        set_bgm_scene(scene)
        last_scene = scene

    # ================================
    # TITLE
    # ================================
    if scene == 0:
        if pyxel.btnp(pyxel.KEY_UP):
            if menu_idx > 0:
                menu_idx -= 1
        if pyxel.btnp(pyxel.KEY_DOWN):
            if menu_idx < len(MENU) - 1:
                menu_idx += 1

        if is_ok_pressed():
            if menu_idx == 0:
                win_streak = 0
                reset_game()
                scene = 1
            else:
                scene = 2

    # ================================
    # GAME
    # ================================
    elif scene == 1:
        phase_timer += 1

        if game_phase == 0:
            if is_ok_pressed():
                game_phase = 1
                phase_timer = 0

        elif game_phase == 1:
            if is_ok_pressed():
                game_phase = 2
                phase_timer = 0

        elif game_phase == 2:
            if is_left_pressed() and hand_cursor > 0:
                hand_cursor -= 1
            if is_right_pressed() and hand_cursor < 2:
                hand_cursor += 1

            if is_ok_pressed():
                player_hand = hand_cursor
                game_phase = 3
                phase_timer = 0

        elif game_phase == 3:
            if is_ok_pressed():
                game_phase = 4
                phase_timer = 0
                result_decided = False

        elif game_phase == 4:
            if phase_timer >= 42 and not result_decided:
                cpu_hand = pyxel.rndi(0, 2)
                diff = (player_hand - cpu_hand + 3) % 3

                if diff == 0:
                    result = 0
                elif diff == 1:
                    result = 1
                else:
                    result = -1

                result_decided = True

            if phase_timer >= 63 and is_ok_pressed():
                if result == 0:
                    game_phase = 10
                elif result == 1:
                    win_streak += 1
                    game_phase = 6
                else:
                    win_streak = 0
                    game_phase = 7

                phase_timer = 0

        elif game_phase == 6:
            show_win_streak = True
            if is_ok_pressed():
                game_phase = 8
                phase_timer = 0

        elif game_phase == 7:
            show_win_streak = False
            if is_ok_pressed():
                scene = 0

        elif game_phase == 8:
            if is_ok_pressed():
                game_phase = 9
                phase_timer = 0

        elif game_phase == 9:
            if is_left_pressed():
                continue_cursor = 0
            if is_right_pressed():
                continue_cursor = 1

            if is_ok_pressed():
                if continue_cursor == 0:
                    game_phase = 1
                    phase_timer = 0
                    result_decided = False
                else:
                    show_win_streak = False
                    scene = 0

        elif game_phase == 10:
            if is_ok_pressed():
                game_phase = 1
                phase_timer = 0

    # ================================
    # HOW TO
    # ================================
    elif scene == 2:
        if is_ok_pressed():
            scene = 0


# ------------------------------
# DRAW GAME
# ------------------------------
def draw_game():
    panel_w = 150
    panel_x = (SCREEN_W - panel_w) // 2
    panel_h = 32
    panel_y = SCREEN_H - panel_h

    pyxel.rect(panel_x, panel_y, panel_w, panel_h, 1)
    pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 7)

    msg_y = panel_y + panel_h // 2 - 3

    # 右上 WIN 表示
    if show_win_streak and win_streak > 0:
        txt = f"WIN {win_streak}"
        pyxel.text(SCREEN_W - len(txt) * 4 - 4, 4, txt, 10)

    # ====== 各フェーズ ======
    if game_phase == 0:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "JANKEN GAME begins!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 1:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "Which hand should I play?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 2:
        slot_w = 40
        start_x = panel_x + (panel_w - slot_w * 3) // 2

        for i, label in enumerate(HAND_LABELS):
            text_x = start_x + i * slot_w + (slot_w - len(label) * 4) // 2
            pyxel.text(text_x, msg_y, label, 7)

            if i == hand_cursor and pyxel.frame_count % 20 < 10:
                tip_x = text_x - 4
                base_x = tip_x - 3
                cy = msg_y + 2
                pyxel.tri(base_x, cy - 2, base_x, cy + 2, tip_x, cy, 7)

    elif game_phase == 3:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "Are you ready?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 4:
        if phase_timer < 21:
            t = "1"
        elif phase_timer < 42:
            t = "2"
        else:
            t = "3!"
        draw_centered_text_panel(panel_x, panel_w, msg_y, t, 7)

        if phase_timer >= 63:
            draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 6:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "You win!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 7:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "You lose...", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 8:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "Continue?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 9:
        draw_centered_text_panel(panel_x, panel_w, msg_y - 6, "Continue?", 7)

        labels = ["YES", "NO"]
        slot_w = 50
        start_x = panel_x + (panel_w - slot_w * 2) // 2
        y = msg_y + 4

        for i, label in enumerate(labels):
            text_x = start_x + i * slot_w + (slot_w - len(label) * 4) // 2
            pyxel.text(text_x, y, label, 7)

            if i == continue_cursor and pyxel.frame_count % 20 < 10:
                tip_x = text_x - 4
                base_x = tip_x - 3
                cy = y + 2
                pyxel.tri(base_x, cy - 2, base_x, cy + 2, tip_x, cy, 7)

    elif game_phase == 10:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "One more time!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)


# ------------------------------
# DRAW
# ------------------------------
def draw():
    pyxel.cls(0)

    if scene == 0:
        draw_centered_text_panel(0, SCREEN_W, 30, "JANKEN GAME", 7)

        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)
            pyxel.rectb(x, y, w, h, 10 if hi else 5)
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, 7 if hi else 6)

            if hi and pyxel.frame_count % 20 < 10:
                cx = x - 6
                cy1 = y + 2
                cy2 = y + h - 2
                cm = (cy1 + cy2) // 2
                pyxel.tri(cx + 4, cm, cx, cy1, cx, cy2, 7)

    elif scene == 1:
        draw_game()

    elif scene == 2:
        draw_centered_text_panel(0, SCREEN_W, 20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Use ARROW or GAMEPAD", 7)
        pyxel.text(10, 60, "- Press ENTER / BUTTONS", 7)
        pyxel.text(10, 80, "Press ENTER / BUTTONS to TITLE", 13)


pyxel.run(update, draw)