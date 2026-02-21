import pyxel

# ==============================
# JS 側の set_bgm_scene を呼べるようにする
# ==============================
try:
    from js import set_bgm_scene as _set_bgm_scene_js

    def set_bgm_scene(scene: int) -> None:
        _set_bgm_scene_js(scene)

except ImportError:
    # ローカル実行用のダミー
    def set_bgm_scene(scene: int) -> None:
        pass


# ==============================
# 基本設定
# ==============================
SCREEN_W = 160
SCREEN_H = 120
pyxel.init(SCREEN_W, SCREEN_H, title="Janken Game", fps=30)
pyxel.mouse(False)

# ==============================
# 日本語フォント（PyxelUniversalFont）
# ==============================
import PyxelUniversalFont as puf

writer = puf.Writer("misaki_gothic.ttf")
JP_FONT_SIZE = 8


def jp_text(x: int, y: int, text: str, col: int, size: int = JP_FONT_SIZE) -> None:
    writer.draw(x, y, text, size, col)


def jp_text_w(text: str, size: int = JP_FONT_SIZE) -> int:
    # 雑に「文字数×サイズ」で幅を取る（今の運用だとこれでOK）
    return len(text) * size


def draw_centered_jp(x0: int, w: int, y: int, text: str, col: int, size: int = JP_FONT_SIZE) -> None:
    x = x0 + (w - jp_text_w(text, size)) // 2
    jp_text(x, y, text, col, size)


# ==============================
# 手アイコン関連
# ==============================
HAND_ICON_SIZE = 16
HAND_IMG_INDEX = [0, 1, 2]  # 0:グー, 1:チョキ, 2:パー


def _load_hand_images() -> None:
    """
    rock.png / scissors.png / paper.png を読み込みつつ、
    左上(0,0)の色を背景色とみなして 0 番色に差し替えて透過させる
    """
    files = ["rock.png", "scissors.png", "paper.png"]

    for i, fname in enumerate(files):
        img = pyxel.image(HAND_IMG_INDEX[i])
        img.load(0, 0, fname)

        bg_col = img.pget(0, 0)
        for y in range(HAND_ICON_SIZE):
            for x in range(HAND_ICON_SIZE):
                if img.pget(x, y) == bg_col:
                    img.pset(x, y, 0)  # 0 = 透過色


def draw_hand_icon(hand: int, x: int, y: int) -> None:
    img_idx = HAND_IMG_INDEX[hand]
    pyxel.blt(x, y, img_idx, 0, 0, 16, 16, 0, 2, 2)


_load_hand_images()

# ==============================
# シーン定義
# ==============================
SCENE_TITLE = 0
SCENE_GAME = 1
SCENE_HOWTO = 2

scene = SCENE_TITLE
last_scene = -1

# ==============================
# タイトルメニュー
# ==============================
menu_idx = 0
MENU = [
    ("スタート", 52, 70, 56, 12),
    ("あそびかた", 52, 86, 56, 12),
]

# ==============================
# GAME フェーズ定義
# ==============================
PHASE_BEGIN = 0          # ゲームスタート！
PHASE_ASK_HAND = 1       # どの手を出す？
PHASE_SELECT_HAND = 2    # 手の選択
PHASE_READY = 3          # 最初はグー（溜め）
PHASE_JKP = 4            # じゃん・けん・ぽん！
PHASE_WIN = 6            # 君の勝ち！
PHASE_LOSE = 7           # 君の負け…
PHASE_NEXT = 8           # 次のゲーム！
PHASE_DRAW = 10          # あいこ！
PHASE_10WIN = 11         # 10連勝！

game_phase = PHASE_BEGIN
phase_timer = 0

# 手 0:グー, 1:チョキ, 2:パー
player_hand = 0
cpu_hand = 0
result = 0              # 1: win, 0: draw, -1: lose
result_decided = False  # ぽん！で勝敗確定したか

hand_cursor = 0
HAND_LABELS = ["グー", "チョキ", "パー"]

# 連勝数 & スコア
win_streak = 0
score = 0
high_score = 0

# スコア表示の状態
score_unlocked = False
score_fade_timer = 0

# シークレットモード（絶対勝てるモード）
cheat_mode = False
secret_index = 0
SECRET_SEQUENCE = ["U", "U", "D", "D", "L", "R", "L", "R", "OK", "OK"]


# ==============================
# 入力ヘルパー
# ==============================
def is_ok_pressed() -> bool:
    return (
        pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y)
    )


def is_left_pressed() -> bool:
    return pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)


def is_right_pressed() -> bool:
    return pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)


def is_up_pressed() -> bool:
    return pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)


def is_down_pressed() -> bool:
    return pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)


# ==============================
# 表示ヘルパー
# ==============================
def draw_next_indicator(panel_x: int, panel_y: int, panel_w: int) -> None:
    """枠の右下に小さな下向き三角を点滅表示"""
    if (pyxel.frame_count % 30) < 15:
        cx = panel_x + panel_w - 10
        top_y = panel_y + 22
        base_y = top_y + 4
        pyxel.tri(cx - 2, top_y, cx + 2, top_y, cx, base_y, 7)


def draw_battle_hands(player_icon_x: int, player_icon_y: int, cpu_icon_y: int) -> None:
    """勝負が決まった後に表示しておくプレイヤー＆CPUの手"""
    draw_hand_icon(player_hand, player_icon_x, player_icon_y)

    img_idx = HAND_IMG_INDEX[cpu_hand]
    pyxel.blt(player_icon_x, cpu_icon_y, img_idx, 0, 0, 16, -16, 0, 2, 2)


def draw_guu_hands(player_icon_x: int, player_icon_y: int, cpu_icon_y: int) -> None:
    """最初はグー用：プレイヤーもCPUもグーを表示"""
    guu = 0
    draw_hand_icon(guu, player_icon_x, player_icon_y)

    img_idx = HAND_IMG_INDEX[guu]
    pyxel.blt(player_icon_x, cpu_icon_y, img_idx, 0, 0, 16, -16, 0, 2, 2)


# ==============================
# リセット
# ==============================
def reset_game() -> None:
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, result_decided
    global win_streak, score
    global score_unlocked, score_fade_timer

    game_phase = PHASE_BEGIN
    phase_timer = 0
    player_hand = 0
    cpu_hand = 0
    result = 0
    hand_cursor = 0
    result_decided = False

    win_streak = 0
    score = 0
    score_unlocked = False
    score_fade_timer = 0


# ==============================
# UPDATE
# ==============================
def update():
    global scene, last_scene, menu_idx
    global game_phase, phase_timer, player_hand, cpu_hand, result
    global hand_cursor, result_decided
    global win_streak, score, high_score
    global score_unlocked, score_fade_timer
    global cheat_mode, secret_index

    # シーンが変わった瞬間だけ BGM 切り替え
    if scene != last_scene:
        if scene == SCENE_TITLE:
            set_bgm_scene(0)
        elif scene == SCENE_GAME:
            set_bgm_scene(1)
        elif scene == SCENE_HOWTO:
            set_bgm_scene(2)
        last_scene = scene

    # HOW TO 画面でのシークレットコマンド入力
    if scene == SCENE_HOWTO:
        key = None
        if is_up_pressed():
            key = "U"
        elif is_down_pressed():
            key = "D"
        elif is_left_pressed():
            key = "L"
        elif is_right_pressed():
            key = "R"
        elif is_ok_pressed():
            key = "OK"

        if key is not None:
            expected = SECRET_SEQUENCE[secret_index]
            if key == expected:
                secret_index += 1
                if secret_index >= len(SECRET_SEQUENCE):
                    cheat_mode = not cheat_mode
                    secret_index = 0
                    scene = SCENE_TITLE
                    menu_idx = 1
            else:
                secret_index = 1 if key == SECRET_SEQUENCE[0] else 0

    # TITLE
    if scene == SCENE_TITLE:
        if is_up_pressed() and menu_idx > 0:
            menu_idx -= 1
        if is_down_pressed() and menu_idx < len(MENU) - 1:
            menu_idx += 1

        if is_ok_pressed():
            if menu_idx == 0:  # スタート
                scene = SCENE_GAME
                reset_game()
            elif menu_idx == 1:  # あそびかた
                scene = SCENE_HOWTO

    # GAME
    elif scene == SCENE_GAME:
        phase_timer += 1

        if game_phase == PHASE_BEGIN:
            if is_ok_pressed():
                game_phase = PHASE_ASK_HAND
                phase_timer = 0

        elif game_phase == PHASE_ASK_HAND:
            if is_ok_pressed():
                game_phase = PHASE_SELECT_HAND
                phase_timer = 0

        elif game_phase == PHASE_SELECT_HAND:
            if is_left_pressed() and hand_cursor > 0:
                hand_cursor -= 1
            if is_right_pressed() and hand_cursor < 2:
                hand_cursor += 1

            if is_ok_pressed():
                player_hand = hand_cursor
                game_phase = PHASE_READY
                phase_timer = 0

        elif game_phase == PHASE_READY:
            if phase_timer >= 30 and is_ok_pressed():
                game_phase = PHASE_JKP
                phase_timer = 0
                result_decided = False

        elif game_phase == PHASE_JKP:
            # ぽん！のタイミングで CPU 手＆勝敗を一度だけ決める
            if phase_timer >= 42 and not result_decided:
                if cheat_mode:
                    # 絶対WIN：プレイヤーが必ず勝つようにCPU決定
                    if player_hand == 0:
                        cpu_hand = 1
                    elif player_hand == 1:
                        cpu_hand = 2
                    else:
                        cpu_hand = 0
                    result = 1
                else:
                    cpu_hand = pyxel.rndi(0, 2)
                    if player_hand == cpu_hand:
                        result = 0
                    elif (
                        (player_hand == 0 and cpu_hand == 1)
                        or (player_hand == 1 and cpu_hand == 2)
                        or (player_hand == 2 and cpu_hand == 0)
                    ):
                        result = 1
                    else:
                        result = -1

                result_decided = True

            # ぽん！が出てから 0.7秒後に OK 受付
            if phase_timer >= 63 and is_ok_pressed():
                if result == 0:
                    game_phase = PHASE_DRAW
                elif result == 1:
                    win_streak += 1
                    score = 2000 if win_streak == 1 else score * 2
                    score_unlocked = True
                    game_phase = PHASE_WIN
                else:
                    if score > high_score:
                        high_score = score
                    game_phase = PHASE_LOSE

                phase_timer = 0

        elif game_phase == PHASE_WIN:
            if is_ok_pressed():
                game_phase = PHASE_10WIN if win_streak >= 10 else PHASE_NEXT
                phase_timer = 0

        elif game_phase == PHASE_LOSE:
            # 負けた瞬間にフェード開始（1回だけ）
            if win_streak > 0 and score_fade_timer == 0:
                score_fade_timer = 15

            if score_fade_timer > 0:
                score_fade_timer -= 1
                if score_fade_timer == 0:
                    win_streak = 0
                    score = 0
                    score_unlocked = False

            if is_ok_pressed():
                scene = SCENE_TITLE
                menu_idx = 0

        elif game_phase == PHASE_NEXT:
            if is_ok_pressed():
                game_phase = PHASE_ASK_HAND
                phase_timer = 0
                result_decided = False

        elif game_phase == PHASE_DRAW:
            if is_ok_pressed():
                game_phase = PHASE_ASK_HAND
                phase_timer = 0
                result_decided = False

        elif game_phase == PHASE_10WIN:
            if is_ok_pressed():
                if score > high_score:
                    high_score = score

                win_streak = 0
                score = 0
                score_unlocked = False
                score_fade_timer = 0

                scene = SCENE_TITLE
                menu_idx = 0

    # HOW TO
    elif scene == SCENE_HOWTO:
        if is_ok_pressed():
            scene = SCENE_TITLE
            # menu_idx は維持


# ==============================
# DRAW (GAME)
# ==============================
def draw_game():
    panel_h = 32
    panel_w = 150
    panel_x = (SCREEN_W - panel_w) // 2
    panel_y = SCREEN_H - panel_h

    # 下パネル
    pyxel.rect(panel_x, panel_y, panel_w, panel_h, 1)
    pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 7)

    msg_center_y = panel_y + panel_h // 2 - 3

    player_icon_x = panel_x + panel_w // 2 - HAND_ICON_SIZE // 2
    player_icon_y = panel_y - HAND_ICON_SIZE - 9

    cpu_icon_y = 9

    # 右上 WIN / SCORE 表示
    show_score = score_unlocked or (score_fade_timer > 0)
    if show_score:
        col_main = 10
        col_score = 7

        if score_fade_timer > 0:
            if score_fade_timer > 10:
                col_main, col_score = 10, 7
            elif score_fade_timer > 5:
                col_main, col_score = 5, 6
            else:
                col_main, col_score = 1, 5

        win_txt = f"WIN {win_streak}"
        pyxel.text(SCREEN_W - len(win_txt) * 4 - 4, 4, win_txt, col_main)

        score_txt = f"SCORE {score}"
        pyxel.text(SCREEN_W - len(score_txt) * 4 - 4, 12, score_txt, col_score)

    # 勝ち系の画面では手を出しっぱなし
    if result_decided and game_phase in (PHASE_WIN, PHASE_NEXT, PHASE_DRAW, PHASE_10WIN):
        draw_battle_hands(player_icon_x, player_icon_y, cpu_icon_y)

    # ===== フェーズ描画 =====
    if game_phase == PHASE_BEGIN:
        draw_centered_jp(panel_x, panel_w, msg_center_y, "ゲームスタート！", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_ASK_HAND:
        draw_centered_jp(panel_x, panel_w, msg_center_y, "どの手を出す？", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_SELECT_HAND:
        slot_w = 40
        start_x = (SCREEN_W - slot_w * 3) // 2
        size = JP_FONT_SIZE

        for i, label in enumerate(HAND_LABELS):
            x = start_x + i * slot_w
            text_x = x + (slot_w - jp_text_w(label, size)) // 2
            jp_text(text_x, msg_center_y, label, 7, size)

            if i == hand_cursor and pyxel.frame_count % 20 < 10:
                tip_x = text_x - 4
                base_x = tip_x - 3
                cy = msg_center_y + 2
                pyxel.tri(base_x, cy - 2, base_x, cy + 2, tip_x, cy, 7)

        draw_hand_icon(hand_cursor, player_icon_x, player_icon_y)

    elif game_phase == PHASE_READY:
        # 「最初はグー」：左から伸びる表示（X位置は完成形の幅で固定）
        if phase_timer < 6:
            shown = ""
        elif phase_timer < 12:
            shown = "最"
        elif phase_timer < 18:
            shown = "最初"
        elif phase_timer < 24:
            shown = "最初は"
        else:
            shown = "最初はグー"

        full_text = "最初はグー"
        size = JP_FONT_SIZE

        # 完成形の幅で中央位置を固定して、shownだけ描く
        x = panel_x + (panel_w - jp_text_w(full_text, size)) // 2
        jp_text(x, msg_center_y, shown, 7, size)

        if phase_timer >= 25:
            draw_guu_hands(player_icon_x, player_icon_y, cpu_icon_y)

        if phase_timer >= 30:
            draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_JKP:
        if phase_timer < 21:
            text = "じゃん"
        elif phase_timer < 42:
            text = "けん"
        else:
            text = "ぽん！"

        draw_centered_jp(panel_x, panel_w, msg_center_y, text, 7)

        if text == "じゃん":
            draw_guu_hands(player_icon_x, player_icon_y, cpu_icon_y)

        if text == "ぽん！":
            draw_battle_hands(player_icon_x, player_icon_y, cpu_icon_y)

        if phase_timer >= 63:
            draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_WIN:
        draw_centered_jp(panel_x, panel_w, msg_center_y, "君の勝ち！", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_LOSE:
        draw_centered_jp(panel_x, panel_w, msg_center_y, "君の負け…", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_NEXT:
        draw_centered_jp(panel_x, panel_w, msg_center_y, "次のゲーム！", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_DRAW:
        draw_centered_jp(panel_x, panel_w, msg_center_y, "あいこ！", 7)
        draw_next_indicator(panel_x, panel_y, panel_w)

    elif game_phase == PHASE_10WIN:
        draw_centered_jp(panel_x, panel_w, msg_center_y, "10連勝！おめでとう！", 10)
        draw_next_indicator(panel_x, panel_y, panel_w)


# ==============================
# DRAW (ALL)
# ==============================
def draw():
    pyxel.cls(0)

    if scene == SCENE_TITLE:
        draw_centered_jp(0, SCREEN_W, 30, "じゃんけんゲーム", 7)

        # HIGH SCORE 表示（英語のままでOKならそのまま）
        if high_score > 0:
            label = "HIGH SCORE"
            pyxel.text(SCREEN_W - len(label) * 4 - 4, 4, label, 10)

            score_txt = str(high_score)
            pyxel.text(SCREEN_W - len(score_txt) * 4 - 4, 12, score_txt, 7)

        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)
            border_col = 10 if hi else 5
            text_col = 7 if hi else 6

            pyxel.rectb(x, y, w, h, border_col)
            draw_centered_jp(x, w, y + 2, label, text_col)

            # ▶ カーソル（点滅）
            if hi and pyxel.frame_count % 20 < 10:
                cx = x - 6
                cy1 = y + 2
                cy2 = y + h - 2
                cm = (cy1 + cy2) // 2
                pyxel.tri(cx + 4, cm, cx, cy1, cx, cy2, 7)

    elif scene == SCENE_GAME:
        draw_game()

    elif scene == SCENE_HOWTO:
        title_col = 8 if cheat_mode else 10

        draw_centered_jp(0, SCREEN_W, 20, "あそびかた", title_col)
        jp_text(10, 50, "・選択：矢印キー / 十字キー", 7)
        jp_text(10, 60, "・決定：Enter / ボタン", 7)
        jp_text(10, 80, "エンター / ボタンでタイトルへ", 13)


pyxel.run(update, draw)