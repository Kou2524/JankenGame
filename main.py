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


def load_hand_images() -> None:
    """
    じゃんけんの手アイコンを image(0) に読み込む
    ファイル名:
      rock.png, scissors.png, paper.png
    """
    pyxel.image(0).load(0, 0, "rock.png")
    pyxel.image(0).load(16, 0, "scissors.png")
    pyxel.image(0).load(32, 0, "paper.png")


# 手画像読み込み
load_hand_images()

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

# 選択カーソル
hand_cursor = 0        # 0〜2
continue_cursor = 0    # 0: YES, 1: NO

HAND_LABELS = ["ROCK", "SCISSORS", "PAPER"]

# 各手のスプライトU座標（image(0) 上）
HAND_SPRITE_U = [0, 16, 32]

# 連勝 & スコア
win_streak = 0
score = 0
max_score = 0
show_win_streak = False  # 一度も勝ってないときは表示しない


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
    """
    タイトルからゲームを開始するときに状態をリセット
    （連勝やスコアもここでクリア）
    """
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, continue_cursor, result_decided
    global win_streak, score, show_win_streak

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
    show_win_streak = False
    # BGM は scene 切り替え時にやるのでここでは呼ばない


def draw_next_indicator(panel_y: int) -> None:
    """
    枠の右下に小さな下向き三角を点滅表示（ミニバージョン）
    """
    if (pyxel.frame_count % 30) < 15:
        cx = SCREEN_W - 10     # 中央X（右寄せ）
        top_y = panel_y + 22   # 一番上のライン
        base_y = top_y + 4     # 下の頂点ライン（少し下）

        # 下向き▼三角（幅4px）
        pyxel.tri(
            cx - 2, top_y,   # 左上
            cx + 2, top_y,   # 右上
            cx, base_y,      # 下の中央（ここが頂点）
            7
        )


def draw_battle_hands(panel_y: int) -> None:
    """
    プレイヤー(左) / CPU(右) の手を表示
    CPU側は 180° 回転して、向かい合ってる感じにする
    """
    # 描画位置（枠の1px上）
    y = panel_y - 1 - 16
    left_x = SCREEN_W // 2 - 8 - 20   # プレイヤー
    right_x = SCREEN_W // 2 - 8 + 20  # CPU

    # プレイヤーの手
    player_u = HAND_SPRITE_U[player_hand]
    pyxel.blt(left_x, y, 0, player_u, 0, 16, 16, 0)

    # CPU の手（16x16 を 180°回転 = 横＆縦反転）
    cpu_u = HAND_SPRITE_U[cpu_hand]
    pyxel.blt(
        right_x + 16,  # 反転描画なので +16, +16 して位置合わせ
        y + 16,
        0,
        cpu_u + 15,    # 元画像の右下から
        15,
        -16,
        -16,
        0,
    )


# ------------------------------
# UPDATE
# ------------------------------
def update():
    global scene, last_scene, menu_idx
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, continue_cursor, result_decided
    global win_streak, score, max_score, show_win_streak

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
            # 「JANKEN GAME begins!」
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
                result_decided = False  # 念のためリセット

        elif game_phase == 4:
            # 1,2,3! フェーズ
            # 0〜20: "1"
            # 21〜41: "2"
            # 42〜: "3!"
            # 3! が出たタイミングで一度だけ CPU 手＆勝敗を決める
            if phase_timer >= 42 and not result_decided:
                cpu_hand = pyxel.rndi(0, 2)

                # じゃんけん判定
                diff = (player_hand - cpu_hand + 3) % 3  # 0:あいこ,1:勝ち,2:負け
                if diff == 0:
                    result = 0
                elif diff == 1:
                    result = 1
                else:
                    result = -1

                result_decided = True

            # 3! が出てから 0.7 秒後（=63フレーム〜）に OK 受付＆結果フェーズへ
            if phase_timer >= 63 and is_ok_pressed():
                if result == 0:
                    # Draw
                    game_phase = 10  # One more time!
                elif result == 1:
                    # Win
                    win_streak += 1
                    if win_streak == 1:
                        score = 2000
                    else:
                        score *= 2  # 倍々ゲーム
                    show_win_streak = True
                    game_phase = 6   # You win!
                else:
                    # Lose
                    win_streak = 0
                    score = 0
                    show_win_streak = False
                    game_phase = 7   # You lose...
                phase_timer = 0

        elif game_phase == 6:
            # 「You win!」 → Continue? へ
            if is_ok_pressed():
                game_phase = 8
                phase_timer = 0

        elif game_phase == 7:
            # 「You lose...」→ タイトルへ（強制終了）
            if is_ok_pressed():
                scene = 0
                menu_idx = 0
                reset_game()

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
                    result_decided = False
                else:  # NO → タイトルへ & MAX SCORE 更新
                    if score > max_score:
                        max_score = score
                    scene = 0
                    menu_idx = 0
                    reset_game()

        elif game_phase == 10:
            # 「One more time!」→ もう一度手選びへ（引き分け）
            if is_ok_pressed():
                game_phase = 1
                phase_timer = 0
                result_decided = False

    # 2: HOW TO
    elif scene == 2:
        if is_ok_pressed():
            scene = 0
            menu_idx = 0


# ------------------------------
# DRAW (GAME)
# ------------------------------
def draw_game():
    # 下パネルの高さ
    panel_h = 32
    panel_y = SCREEN_H - panel_h

    # 枠の幅：150px（中央に配置）
    panel_w = 150
    panel_x = (SCREEN_W - panel_w) // 2

    # 下パネル
    pyxel.rect(panel_x, panel_y, panel_w, panel_h, 1)    # 中
    pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 7)   # 枠

    # 枠のちょうど中央に来るY（文字高さ6px前提）
    msg_center_y = panel_y + panel_h // 2 - 3

    # 右上 WIN / SCORE 表示
    if show_win_streak and win_streak > 0:
        win_txt = f"WIN {win_streak}"
        win_x = SCREEN_W - len(win_txt) * 4 - 4
        pyxel.text(win_x, 4, win_txt, 10)

        score_txt = f"SCORE {score}"
        score_x = SCREEN_W - len(score_txt) * 4 - 4
        pyxel.text(score_x, 12, score_txt, 7)

    # ===== 各フェーズ =====
    if game_phase == 0:
        draw_centered_text(msg_center_y, "JANKEN GAME begins!", 7)
        draw_next_indicator(panel_y)

    elif game_phase == 1:
        draw_centered_text(msg_center_y, "Which hand should I play?", 7)
        draw_next_indicator(panel_y)

    elif game_phase == 2:
        # 手の選択肢：1行まるごと中央揃え
        slot_w = 40
        start_x = (SCREEN_W - slot_w * 3) // 2

        for i, label in enumerate(HAND_LABELS):
            x = start_x + i * slot_w
            text_x = x + (slot_w - len(label) * 4) // 2
            label_y = msg_center_y
            pyxel.text(text_x, label_y, label, 7)

            # 選択中に三角カーソル（点滅・3px幅）
            if i == hand_cursor and pyxel.frame_count % 20 < 10:
                tip_x = text_x - 4          # テキストとの隙間4px
                base_x = tip_x - 3          # 横幅3px
                cy = label_y + 2            # 文字と揃うように微調整

                # 右向きの小さな三角（幅3px・高さ4px）
                pyxel.tri(base_x, cy - 2, base_x, cy + 2, tip_x, cy, 7)

        # ★ 選択中の手のプレビュー（枠の1px上、中央）
        hand_u = HAND_SPRITE_U[hand_cursor]
        preview_x = SCREEN_W // 2 - 8          # 16px の半分だけ左に
        preview_y = panel_y - 1 - 16           # 枠の1px上に16pxの画像
        pyxel.blt(preview_x, preview_y, 0, hand_u, 0, 16, 16, 0)

    elif game_phase == 3:
        draw_centered_text(msg_center_y, "Are you ready?", 7)
        draw_next_indicator(panel_y)

    elif game_phase == 4:
        # 1,2,3! の表示（0.7秒＝21フレーム間隔）
        if phase_timer < 21:
            text = "1"
        elif phase_timer < 42:
            text = "2"
        else:
            text = "3!"
        draw_centered_text(msg_center_y, text, 7)

        # 3! が出て勝敗が決まった後は、両手を表示
        if phase_timer >= 42 and result_decided:
            draw_battle_hands(panel_y)

        # 3! が出てから0.7秒後に ▼ 点滅開始
        if phase_timer >= 63:
            draw_next_indicator(panel_y)

    elif game_phase == 6:
        # 勝ち画面：両手＋メッセージ
        draw_battle_hands(panel_y)
        draw_centered_text(msg_center_y, "You win!", 7)
        draw_next_indicator(panel_y)

    elif game_phase == 7:
        # 負け画面：両手は出さず、メッセージのみ
        draw_centered_text(msg_center_y, "You lose...", 7)
        draw_next_indicator(panel_y)

    elif game_phase == 8:
        # Continue? だけ表示（両手も出しっぱにする）
        draw_battle_hands(panel_y)
        draw_centered_text(msg_center_y, "Continue?", 7)
        draw_next_indicator(panel_y)

    elif game_phase == 9:
        # Continue? を少し上、その下に YES / NO ＋両手
        draw_battle_hands(panel_y)

        cont_y = msg_center_y - 6
        draw_centered_text(cont_y, "Continue?", 7)

        labels = ["YES", "NO"]
        slot_w = 45
        start_x = (SCREEN_W - slot_w * 2) // 2
        yesno_y = msg_center_y + 4

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
        draw_centered_text(msg_center_y, "One more time!", 7)
        draw_next_indicator(panel_y)


# ------------------------------
# DRAW (ALL)
# ------------------------------
def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== TITLE =====
        draw_centered_text(30, "JANKEN GAME", 7)

        # MAX SCORE 表示（あれば）
        if max_score > 0:
            label = "MAX SCORE"
            label_x = SCREEN_W - len(label) * 4 - 4
            pyxel.text(label_x, 16, label, 10)

            score_txt = f"{max_score}"
            score_x = SCREEN_W - len(score_txt) * 4 - 4
            pyxel.text(score_x, 24, score_txt, 7)

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