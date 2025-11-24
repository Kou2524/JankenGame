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

# 手アイコン（16x16）
# 0: ROCK, 1: SCISSORS, 2: PAPER
pyxel.image(0).load(0, 0, "rock.png")
pyxel.image(0).load(16, 0, "scissors.png")
pyxel.image(0).load(32, 0, "paper.png")

def draw_hand_icon_center(hand: int, y: int) -> None:
    """hand(0〜2) を画面中央に16x16で描画"""
    if hand < 0 or hand > 2:
        return
    u = hand * 16
    x = SCREEN_W // 2 - 8
    # 黒(0)を透過色扱い
    pyxel.blt(x, y, 0, u, 0, 16, 16, 0)


# 0: TITLE, 1: GAME, 2: HOW TO
scene = 0
last_scene = -1  # 直前のシーン（BGM切り替え用）

# タイトルメニュー
menu_idx = 0  # 0: START, 1: HOW TO
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 52, 86, 56, 12),
]

# ===== GAME 用の状態管理 =====
# 0: Janken game begins!
# 1: Which hand should I play?
# 2: 手の選択
# 3: Are you ready?
# 4: 1,2,3!
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
result_decided = False  # 3! のタイミングで勝敗を決めたかどうか

# 連勝数 & スコア
win_streak = 0
score = 0
max_score = 0

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


def draw_centered_text_panel(panel_x: int, panel_w: int, msg_y: int, text: str, col: int) -> None:
    text_w = len(text) * 4
    x = panel_x + (panel_w - text_w) // 2
    pyxel.text(x, msg_y, text, col)


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
    """
    NEW GAME 開始時に状態をリセット
    """
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, continue_cursor, result_decided
    global win_streak, score

    game_phase = 0
    phase_timer = 0
    player_hand = 0
    cpu_hand = 0
    result = 0
    hand_cursor = 0
    continue_cursor = 0
    result_decided = False
    win_streak = 0
    score = 0
    # max_score はリセットしない（タイトルに残す）


def draw_next_indicator(panel_x: int, panel_y: int, panel_w: int) -> None:
    """
    枠の右下に小さな下向き三角を点滅表示（ミニバージョン）
    """
    if (pyxel.frame_count % 30) < 15:
        cx = panel_x + panel_w - 10  # 枠の中で右寄せ
        top_y = panel_y + 22         # 一番上のライン
        base_y = top_y + 4           # 下の頂点ライン（少し下）

        # 下向き▼三角（幅4px）
        pyxel.tri(
            cx - 2, top_y,   # 左上
            cx + 2, top_y,   # 右上
            cx, base_y,      # 下の中央（ここが頂点）
            7
        )


# ------------------------------
# UPDATE
# ------------------------------
def update():
    global scene, last_scene, menu_idx
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, continue_cursor, result_decided
    global win_streak, score, max_score

    # === シーンが変わった瞬間だけ BGM を切り替える ===
    if scene != last_scene:
        if scene == 0:
            set_bgm_scene(0)  # タイトル用BGM
        elif scene == 1:
            set_bgm_scene(1)  # ゲーム用BGM
        elif scene == 2:
            set_bgm_scene(2)  # HOW TO用BGM（bgm1 を使うなら JS 側で同じにしてOK）
        last_scene = scene

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
                result_decided = False

        elif game_phase == 4:
            # 1,2,3! フェーズ
            # 0〜20: "1"
            # 21〜41: "2"
            # 42〜 : "3!"
            # 3! が出たタイミング(>=42)で一度だけ CPU の手＆結果を計算
            if phase_timer >= 42 and not result_decided:
                cpu_hand = pyxel.rndi(0, 2)

                diff = (player_hand - cpu_hand + 3) % 3  # 0:あいこ, 1:勝ち, 2:負け
                if diff == 0:
                    result = 0
                elif diff == 1:
                    result = 1
                else:
                    result = -1

                result_decided = True

            # 3! が出てから 0.7 秒後（=63フレーム〜）に OK 受付
            # このタイミングで初めて win_streak / score を更新する
            if phase_timer >= 63 and is_ok_pressed():
                if result == 0:
                    # あいこ → そのまま次のラウンドへ（スコア変化なし）
                    game_phase = 10
                elif result == 1:
                    # 勝ち
                    win_streak += 1
                    score = 2000 * (2 ** (win_streak - 1))
                    game_phase = 6
                else:
                    # 負け → ストリーク終了 & スコア0
                    win_streak = 0
                    score = 0
                    game_phase = 7

                phase_timer = 0

        elif game_phase == 6:
            # 「You win!」 → ボタンで Continue? へ
            if is_ok_pressed():
                game_phase = 8
                phase_timer = 0

        elif game_phase == 7:
            # 「You lose...」→ OK でタイトルへ（MAX SCORE は更新しない）
            if is_ok_pressed():
                scene = 0
                menu_idx = 0

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
                if continue_cursor == 0:  # YES → 連勝続行
                    game_phase = 1
                    phase_timer = 0
                else:  # NO → この時点の score で MAX 更新してタイトルへ
                    if score > 0 and score > max_score:
                        max_score = score
                    win_streak = 0
                    score = 0
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
    # 下パネルのサイズ
    panel_h = 32
    panel_w = 150
    panel_x = (SCREEN_W - panel_w) // 2
    panel_y = SCREEN_H - panel_h

    # 下パネル
    pyxel.rect(panel_x, panel_y, panel_w, panel_h, 1)    # 中
    pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 7)   # 枠

    # 枠のちょうど中央に来るY（文字高さ6px前提）
    msg_y = panel_y + panel_h // 2 - 3

    # 右上 WIN / SCORE 表示（連勝しているときだけ）
    if win_streak > 0:
        win_txt = f"WIN {win_streak}"
        win_x = SCREEN_W - len(win_txt) * 4 - 4
        pyxel.text(win_x, 4, win_txt, 10)

        score_txt = f"SCORE {score}"
        score_x = SCREEN_W - len(score_txt) * 4 - 4
        pyxel.text(score_x, 12, score_txt, 7)

    # ====== 各フェーズ ======
    if game_phase == 0:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "JANKEN GAME begins!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 1:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "Which hand should I play?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 2:
        # 選択中の手アイコン（パネルの少し上）
        icon_y = panel_y - 18
        draw_hand_icon_center(hand_cursor, icon_y)

        # 手の選択肢：1行まるごと中央揃え
        slot_w = 40
        start_x = panel_x + (panel_w - slot_w * 3) // 2

        for i, label in enumerate(HAND_LABELS):
            x = start_x + i * slot_w
            text_x = x + (slot_w - len(label) * 4) // 2
            label_y = msg_y
            pyxel.text(text_x, label_y, label, 7)

            # 選択中に三角カーソル（点滅・3px幅）
            if i == hand_cursor and pyxel.frame_count % 20 < 10:
                tip_x = text_x - 4          # テキストとの隙間4px
                base_x = tip_x - 3          # 横幅3px
                cy = label_y + 2            # 文字と揃うように微調整

                # 右向きの小さな三角（幅3px・高さ4px）
                pyxel.tri(base_x, cy - 2, base_x, cy + 2, tip_x, cy, 7)

    elif game_phase == 3:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "Are you ready?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 4:
        # プレイヤー & CPU の手アイコン表示（3! のタイミング）
        player_y = panel_y - 18
        cpu_y = player_y - 20
        draw_hand_icon_center(cpu_hand, cpu_y)
        draw_hand_icon_center(player_hand, player_y)

        # 1,2,3! の表示（0.7秒＝21フレーム間隔）
        if phase_timer < 21:
            text = "1"
        elif phase_timer < 42:
            text = "2"
        else:
            text = "3!"
        draw_centered_text_panel(panel_x, panel_w, msg_y, text, 7)

        # 3! が出てから0.7秒後に ▼ 点滅開始
        if phase_timer >= 63:
            draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 6:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "You win!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 7:
        # 負けた瞬間に win_streak / score は 0 にしているので右上は何も表示されない
        draw_centered_text_panel(panel_x, panel_w, msg_y, "You lose...", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 8:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "Continue?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 9:
        # Continue? を少し上、その下に YES / NO
        cont_y = msg_y - 6
        draw_centered_text_panel(panel_x, panel_w, cont_y, "Continue?", 7)

        labels = ["YES", "NO"]
        slot_w = 45
        start_x = panel_x + (panel_w - slot_w * 2) // 2
        yesno_y = msg_y + 4

        for i, label in enumerate(labels):
            x = start_x + i * slot_w
            text_x = x + (slot_w - len(label) * 4) // 2
            pyxel.text(text_x, yesno_y, label, 7)

            # 点滅カーソル（3px三角＋1文字分スペース）
            if i == continue_cursor and pyxel.frame_count % 20 < 10:
                tip_x = text_x - 4      # テキスト左に4pxあける
                base_x = tip_x - 3      # 横幅3px
                cy = yesno_y + 2        # 文字と揃うように微調整

                pyxel.tri(base_x, cy - 2, base_x, cy + 2, tip_x, cy, 7)

    elif game_phase == 10:
        draw_centered_text_panel(panel_x, panel_w, msg_y, "One more time!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)


# ------------------------------
# DRAW (ALL)
# ------------------------------
def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== TITLE =====
        draw_centered_text(30, "JANKEN GAME", 7)

        # MAX SCORE 表示（右上・2行）
        if max_score > 0:
            label = "MAX SCORE"
            label_x = SCREEN_W - len(label) * 4 - 4
            value = str(max_score)
            value_x = SCREEN_W - len(value) * 4 - 4

            pyxel.text(label_x, 4, label, 10)
            pyxel.text(value_x, 12, value, 7)

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