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

# ==== 手アイコン関連 ====
HAND_ICON_SIZE = 16
HAND_IMG_INDEX = [0, 1, 2]  # ROCK, SCISSORS, PAPER


def _load_hand_images():
    """
    rock.png / scissors.png / paper.png を読み込みつつ、
    左上(0,0)の色を背景色とみなして 0 番色に差し替えて透過させる
    """
    files = ["rock.png", "scissors.png", "paper.png"]

    for i, fname in enumerate(files):
        img = pyxel.image(HAND_IMG_INDEX[i])
        img.load(0, 0, fname)

        # 左上の色を背景色とみなす
        bg_col = img.pget(0, 0)
        for y in range(HAND_ICON_SIZE):
            for x in range(HAND_ICON_SIZE):
                if img.pget(x, y) == bg_col:
                    img.pset(x, y, 0)  # 0 = 透過色にする


def draw_hand_icon(hand: int, x: int, y: int):
    """指定した手アイコンを (x, y) に描画"""
    img_idx = HAND_IMG_INDEX[hand]
    pyxel.blt(x, y, img_idx, 0, 0, 16, 16, 0, 2, 2)


# 画像を読み込む
_load_hand_images()

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

# 連勝数 & スコア
win_streak = 0
score = 0
high_score = 0  # タイトル画面で表示するハイスコア

# スコア表示の状態
score_unlocked = False      # 一度でも「You win!」を出したら True
score_fade_timer = 0        # 負けたときのフェード用タイマー

# ------------------------------
# ヘルパー
# ------------------------------
def draw_centered_text_screen(y: int, text: str, col: int) -> None:
    text_w = len(text) * 4
    x = (SCREEN_W - text_w) // 2
    pyxel.text(x, y, text, col)


def draw_centered_text_panel(panel_x: int, panel_w: int, y: int, text: str, col: int) -> None:
    text_w = len(text) * 4
    x = panel_x + (panel_w - text_w) // 2
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
    ゲーム開始時に状態をリセット
    """
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, continue_cursor, result_decided
    global win_streak, score
    global score_unlocked, score_fade_timer  # ★ここ追加

    game_phase = 0
    phase_timer = 0
    player_hand = 0
    cpu_hand = 0
    result = 0
    hand_cursor = 0
    continue_cursor = 0
    result_decided = False

    # 連勝・スコアもリセット
    win_streak = 0
    score = 0
    score_unlocked = False      # ★追加
    score_fade_timer = 0        # ★追加


def draw_next_indicator(panel_x: int, panel_y: int, panel_w: int) -> None:
    """
    枠の右下に小さな下向き三角を点滅表示（ミニバージョン）
    """
    if (pyxel.frame_count % 30) < 15:
        cx = panel_x + panel_w - 10  # 右寄せ
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
    global win_streak, score, high_score
    global score_unlocked, score_fade_timer

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
                result_decided = False  # 念のためリセット

        elif game_phase == 4:
            # 1,2,3! フェーズ

            # 3! が出たタイミングで一度だけ CPU 手＆勝敗を決める
            if phase_timer >= 42 and not result_decided:
                cpu_hand = pyxel.rndi(0, 2)

                # 手の意味
                # 0: ROCK, 1: SCISSORS, 2: PAPER

                if player_hand == cpu_hand:
                    result = 0  # draw
                elif (
                    (player_hand == 0 and cpu_hand == 1)  # ROCK beats SCISSORS
                    or (player_hand == 1 and cpu_hand == 2)  # SCISSORS beats PAPER
                    or (player_hand == 2 and cpu_hand == 0)  # PAPER beats ROCK
                ):
                    result = 1  # win
                else:
                    result = -1  # lose

                result_decided = True

            # 3! が出てから 0.7秒後に OK 受付
            if phase_timer >= 63 and is_ok_pressed():
                if result == 0:
                    # あいこ：スコアも連勝もそのまま
                    game_phase = 10  # One more time!

                elif result == 1:
                    # ★ここで初めてスコア＆連勝を更新
                    win_streak += 1
                    if win_streak == 1:
                        score = 2000
                    else:
                        score *= 2

                    score_unlocked = True   # 表示解禁（1回目の勝ちのとき）

                    game_phase = 6          # You win!

                else:
                    # 負け：スコアはいじらず、game_phase==7 でフェード処理
                    game_phase = 7          # You lose...

                phase_timer = 0

        elif game_phase == 6:
            # 「You win!」 → Continue? へ
            if is_ok_pressed():
                game_phase = 8
                phase_timer = 0

        elif game_phase == 7:
            # 「You lose...」

            # ★負けた瞬間にフェード開始（1回だけ）
            if win_streak > 0 and score_fade_timer == 0:
                score_fade_timer = 15  # 30フレーム＝約0.5秒くらい

            # フェードタイマー進行
            if score_fade_timer > 0:
                score_fade_timer -= 1
                # フェードが終わったら実際にリセット
                if score_fade_timer == 0:
                    win_streak = 0
                    score = 0
                    score_unlocked = False

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
                if continue_cursor == 0:  # YES
                    game_phase = 1
                    phase_timer = 0
                    result_decided = False
                else:  # NO → ここでハイスコア更新
                    if score > high_score:
                        high_score = score
                    scene = 0
                    menu_idx = 0

        elif game_phase == 10:
            # 「One more time!」→ もう一度手選びへ
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
    # 下パネルの高さ・幅
    panel_h = 32
    panel_w = 150
    panel_x = (SCREEN_W - panel_w) // 2
    panel_y = SCREEN_H - panel_h

    # 下パネル
    pyxel.rect(panel_x, panel_y, panel_w, panel_h, 1)    # 中
    pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 7)   # 枠
    
    # 画面中央（手を真ん中に置く用）
    center_x = SCREEN_W // 2 - 16  # 32pxの半分
    center_y = SCREEN_H // 2 - 16

    # 枠のちょうど中央に来るY（文字高さ6px前提）
    msg_center_y = panel_y + panel_h // 2 - 3

    # 手アイコンの位置（プレイヤー）
    player_icon_x = panel_x + panel_w // 2 - HAND_ICON_SIZE // 2
    player_icon_y = panel_y - HAND_ICON_SIZE - 9
    # CPUアイコン（プレイヤーの上側）
    cpu_icon_x = player_icon_x
    cpu_icon_y = player_icon_y - HAND_ICON_SIZE - 4

    # 右上 WIN / SCORE 表示
    # - score_unlocked が True になったら、負けてフェードが終わるまでずっと表示
    # - 負けたあとは score_fade_timer でゆっくり消える
    show_score = score_unlocked or (score_fade_timer > 0)

    if show_score:
        col_main = 10   # WIN
        col_score = 7   # SCORE

        # フェード中はだんだん暗くする（既に入れてるならそれ流用でOK）
        if score_fade_timer > 0:
            if score_fade_timer > 10:      # 明るい（最初の1/3）
                col_main = 10
                col_score = 7
            elif score_fade_timer > 5:     # 中くらい（中盤1/3）
                col_main = 5
                col_score = 6
            else:                          # 暗い（ラスト1/3）
                col_main = 1
                col_score = 5

        win_txt = f"WIN {win_streak}"
        win_x = SCREEN_W - len(win_txt) * 4 - 4
        pyxel.text(win_x, 4, win_txt, col_main)

        score_txt = f"SCORE {score}"
        score_x = SCREEN_W - len(score_txt) * 4 - 4
        pyxel.text(score_x, 12, score_txt, col_score)

    # ===== 各フェーズ =====
    if game_phase == 0:
        draw_centered_text_panel(panel_x, panel_w, msg_center_y, "JANKEN GAME begins!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 1:
        draw_centered_text_panel(panel_x, panel_w, msg_center_y, "Which hand should I play?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

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

        # 選択中の手アイコンをパネルの真上に表示
        draw_hand_icon(hand_cursor, player_icon_x, player_icon_y)

    elif game_phase == 3:
        # 「Are you ready?」画面
        draw_centered_text_panel(
            panel_x,
            panel_w,
            msg_center_y,       # ← ここ追加（真ん中のY座標）
            "Are you ready?",   # ← テキスト
            7                   # ← 色（白っぽい色、他のフェーズと合わせてOK）
        )
        draw_next_indicator(panel_x, panel_y, panel_w)
    
    elif game_phase == 4:
        # 1,2,3! の表示 (0.7秒 = 21フレーム間隔)
        if phase_timer < 21:
            text = "1"
        elif phase_timer < 42:
            text = "2"
        else:
            text = "3!"
        
        # 数字（1,2,3!）をセンター表示
        draw_centered_text_panel(panel_x, panel_w, msg_center_y, text, 7)

        # 🔥 3! のときだけ、手を表示
        if text == "3!":
            # ▼ プレイヤーの手：選択フェーズと同じ位置
            draw_hand_icon(player_hand, player_icon_x, player_icon_y)

            # ▼ CPU の手：画面最上部から 1px 下に、上下逆で表示
            img_idx = HAND_IMG_INDEX[cpu_hand]
            cpu_x = player_icon_x
            cpu_y = 1  # 画面最上部から 1px 下

            # h を -16 にすると上下反転（16 は HAND_ICON_SIZE と同じ）
            pyxel.blt(cpu_x, cpu_y, img_idx, 0, 0, 16, -16, 0, 2, 2)

        # 3! が出てから0.7秒後に ▶ 点滅開始（今まで通り）
        if phase_timer >= 63:
            draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 6:
        draw_centered_text_panel(panel_x, panel_w, msg_center_y, "You win!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 7:
        draw_centered_text_panel(panel_x, panel_w, msg_center_y, "You lose...", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 8:
        draw_centered_text_panel(panel_x, panel_w, msg_center_y, "Continue?", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == 9:
        # Continue? を少し上、その下に YES / NO
        cont_y = msg_center_y - 6
        draw_centered_text_panel(panel_x, panel_w, cont_y, "Continue?", 7)

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
        draw_centered_text_panel(panel_x, panel_w, msg_center_y, "One more time!", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)


# ------------------------------
# DRAW (ALL)
# ------------------------------
def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== TITLE =====
        draw_centered_text_screen(30, "JANKEN GAME", 7)

        # HIGH SCORE 表示（あれば）
        if high_score > 0:
            label = "HIGH SCORE"
            label_x = SCREEN_W - len(label) * 4 - 4
            pyxel.text(label_x, 4, label, 10)

            score_txt = str(high_score)
            score_x = SCREEN_W - len(score_txt) * 4 - 4
            pyxel.text(score_x, 12, score_txt, 7)

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
        draw_centered_text_screen(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Use ARROW or GAMEPAD", 7)
        pyxel.text(10, 60, "- Press ENTER / BUTTONS", 7)
        pyxel.text(10, 80, "Press ENTER / BUTTONS to TITLE", 13)


pyxel.run(update, draw)