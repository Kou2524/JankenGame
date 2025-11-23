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

# タイトルメニュー
menu_idx = 0  # 0: START, 1: HOW TO
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 48, 86, 64, 12),
]

# ===== GAME 用の状態管理 =====
# 0: Janken game begins!
# 1: Which hand should I play?
# 2: 手の選択
# 3: Are you ready?
# 4: 1,2,3!
# 5: 結果計算＆分岐
# 6: You win!
# 7: You lose...
# 8: Continue?
# 9: Yes / No 選択
# 10: One more time!
game_phase = 0
phase_timer = 0  # そのフェーズに入ってからの経過フレーム

# 手 0: ROCK, 1: SCISSORS, 2: PAPER
player_hand = 0
cpu_hand = 0
result = 0  # 1: win, 0: draw, -1: lose

# 選択カーソル
hand_cursor = 0        # 0〜2
continue_cursor = 0    # 0: YES, 1: NO

HAND_LABELS = ["ROCK", "SCISSORS", "PAPER"]


# ------------------------------
# ヘルパー
# ------------------------------
def draw_centered_text(y: int, text: str, col: int) -> None:
    text_w = len(text) * 4
    x = (SCREEN_W - text_w) // 2
    pyxel.text(x, y, text, col)


def is_ok_pressed() -> bool:
    # A / B / X / Y / ENTER / SPACE
    return (
        pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
    )


def is_left_pressed() -> bool:
    return (
        pyxel.btnp(pyxel.KEY_LEFT)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
    )


def is_right_pressed() -> bool:
    return (
        pyxel.btnp(pyxel.KEY_RIGHT)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
    )


def reset_game() -> None:
    global game_phase, phase_timer, player_hand, cpu_hand, result, hand_cursor, continue_cursor
    game_phase = 0
    phase_timer = 0
    player_hand = 0
    cpu_hand = 0
    result = 0
    hand_cursor = 0
    continue_cursor = 0
    set_bgm_scene(1)  # 必要なら GAME 用BGM


# ------------------------------
# UPDATE
# ------------------------------
def update():
    global scene, menu_idx
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, continue_cursor

    # タイトルにいる時だけBGMを切り替え
    if scene == 0:
        set_bgm_scene(0)

    # 0: TITLE
    if scene == 0:
        # メニュー移動（上下、ループなし）
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            if menu_idx > 0:
                menu_idx -= 1

        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            if menu_idx < len(MENU) - 1:
                menu_idx += 1

        # 決定
        if is_ok_pressed():
            if menu_idx == 0:  # START
                scene = 1
                reset_game()
            elif menu_idx == 1:  # HOW TO
                scene = 2

    # 1: GAME
    elif scene == 1:
        phase_timer += 1

        if game_phase == 0:
            # 「Janken game begins!」
            if is_ok_pressed():
                game_phase = 1
                phase_timer = 0

        elif game_phase == 1:
            # 「Which hand should I play?」
            if is_ok_pressed():
                game_phase = 2
                phase_timer = 0

        elif game_phase == 2:
            # 手の選択
            if is_left_pressed() and hand_cursor > 0:
                hand_cursor -= 1
            if is_right_pressed() and hand_cursor < 2:
                hand_cursor += 1

            if is_ok_pressed():
                player_hand = hand_cursor
                game_phase = 3
                phase_timer = 0

        elif game_phase == 3:
            # 「Are you ready?」
            if is_ok_pressed():
                game_phase = 4
                phase_timer = 0

        elif game_phase == 4:
            # 「1, 2, 3!」
            # 表示は draw 側で、一定時間経過後にOK受付
            # 0.6sごと → 18フレーム（fps=30）
            # 3! のあと 1秒(30フレーム)待ってからOK
            ready_frame = 18 * 3 + 30  # 84フレーム
            if phase_timer >= ready_frame and is_ok_pressed():
                game_phase = 5
                phase_timer = 0

        elif game_phase == 5:
            # 結果計算 → 即分岐
            cpu_hand = pyxel.rndi(0, 2)

            # (player - cpu + 3) % 3
            # 0: あいこ, 1: 勝ち, 2: 負け
            diff = (player_hand - cpu_hand + 3) % 3
            if diff == 0:
                result = 0
                game_phase = 10  # One more time!
            elif diff == 1:
                result = 1
                game_phase = 6   # You win!
            else:
                result = -1
                game_phase = 7   # You lose...

            phase_timer = 0

        elif game_phase == 6:
            # 「You win!」 → タイトルへ
            if is_ok_pressed():
                scene = 0
                menu_idx = 0

        elif game_phase == 7:
            # 「You lose...」
            if is_ok_pressed():
                game_phase = 8
                phase_timer = 0

        elif game_phase == 8:
            # 「Continue?」→ ボタンで YES/NO 選択へ
            if is_ok_pressed():
                game_phase = 9
                phase_timer = 0

        elif game_phase == 9:
            # YES / NO 選択
            if is_left_pressed():
                continue_cursor = 0
            if is_right_pressed():
                continue_cursor = 1

            if is_ok_pressed():
                if continue_cursor == 0:  # YES
                    game_phase = 1
                    phase_timer = 0
                else:  # NO
                    scene = 0
                    menu_idx = 0

        elif game_phase == 10:
            # 「One more time!」→ もう一度手選びへ
            if is_ok_pressed():
                game_phase = 1
                phase_timer = 0

    # 2: HOW TO
    elif scene == 2:
        if is_ok_pressed():
            scene = 0
            menu_idx = 0


# ------------------------------
# DRAW (GAME)
# ------------------------------
def draw_game():
    # 下パネルの高さを少し広げる
    panel_h = 32
    panel_y = SCREEN_H - panel_h

    # 下パネル
    pyxel.rect(0, panel_y, SCREEN_W, panel_h, 1)    # 中
    pyxel.rectb(0, panel_y, SCREEN_W, panel_h, 7)   # 枠

    # 上側（ゲームエリア）仮タイトル
    draw_centered_text(30, "JANKEN GAME", 7)

    # 下パネル内のベースY
    msg_y = panel_y + 6

    if game_phase == 0:
        draw_centered_text(msg_y, "Janken game begins!", 7)

    elif game_phase == 1:
        draw_centered_text(msg_y, "Which hand should I play?", 7)

    elif game_phase == 2:
        # 手の選択肢だけ表示（Rock Paper Scissors の文字は消す）
        slot_w = 40
        start_x = (SCREEN_W - slot_w * 3) // 2

        for i, label in enumerate(HAND_LABELS):
            x = start_x + i * slot_w
            text_x = x + (slot_w - len(label) * 4) // 2
            pyxel.text(text_x, msg_y + 4, label, 7)

            # 選択中に三角カーソル（点滅）
            if i == hand_cursor and pyxel.frame_count % 20 < 10:
                tri_x = text_x - 6
                tri_y1 = msg_y + 3
                tri_y2 = msg_y + 11
                tri_m = (tri_y1 + tri_y2) // 2
                pyxel.tri(tri_x + 4, tri_m, tri_x, tri_y1, tri_x, tri_y2, 7)

    elif game_phase == 3:
        draw_centered_text(msg_y, "Are you ready?", 7)

    elif game_phase == 4:
        # 1,2,3! の表示（0.6秒＝18フレーム間隔）
        if phase_timer < 18:
            text = "1"
        elif phase_timer < 36:
            text = "2"
        else:
            text = "3!"
        draw_centered_text(msg_y, text, 7)

    elif game_phase == 6:
        draw_centered_text(msg_y, "You win!", 7)

    elif game_phase == 7:
        draw_centered_text(msg_y, "You lose...", 7)

    elif game_phase == 8:
        draw_centered_text(msg_y, "Continue?", 7)

    elif game_phase == 9:
        # YES / NO 選択（枠を広げて収める）
        draw_centered_text(msg_y, "Continue?", 7)

        labels = ["YES", "NO"]
        slot_w = 45
        start_x = (SCREEN_W - slot_w * 2) // 2

        for i, label in enumerate(labels):
            x = start_x + i * slot_w
            text_x = x + (slot_w - len(label) * 4) // 2
            pyxel.text(text_x, msg_y + 12, label, 7)

            # 点滅カーソル
            if i == continue_cursor and pyxel.frame_count % 20 < 10:
                tri_x = text_x - 6
                tri_y1 = msg_y + 11
                tri_y2 = msg_y + 19
                tri_m = (tri_y1 + tri_y2) // 2
                pyxel.tri(tri_x + 4, tri_m, tri_x, tri_y1, tri_x, tri_y2, 7)

    elif game_phase == 10:
        draw_centered_text(msg_y, "One more time!", 7)


# ------------------------------
# DRAW (ALL)
# ------------------------------
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

    elif scene == 1:
        # ===== GAME =====
        draw_game()

    elif scene == 2:
        # ===== HOW TO =====
        draw_centered_text(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Use ARROW or GAMEPAD", 7)
        pyxel.text(10, 60, "- Press ENTER / BUTTONS", 7)
        pyxel.text(10, 80, "Press ENTER / BUTTONS to TITLE", 13)


pyxel.run(update, draw)
