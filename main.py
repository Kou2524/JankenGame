import random
import pyxel

# ===== JS 側の set_bgm_scene を呼べるようにする =====
try:
    from js import set_bgm_scene as _set_bgm_scene_js

    def set_bgm_scene(scene: int) -> None:
        _set_bgm_scene_js(scene)

except ImportError:
    # ローカル実行用ダミー
    def set_bgm_scene(scene: int) -> None:
        pass


# ===== 画面設定 =====
SCREEN_W = 160
SCREEN_H = 120

pyxel.init(SCREEN_W, SCREEN_H, title="Janken Game", fps=30)
pyxel.mouse(False)

# ===== 手アイコン画像設定 =====
HAND_ICON_SIZE = 16  # 元画像サイズ
# 0: ROCK, 1: SCISSORS, 2: PAPER
HAND_IMG_INDEX = [0, 1, 2]


def _load_hand_images() -> None:
    """
    hand_rock.png, hand_scissors.png, hand_paper.png を
    それぞれ image(0), image(1), image(2) に読み込む。
    左上の色を背景色とみなして 0(透明) に置き換える。
    """
    filenames = [
        "hand_rock.png",
        "hand_scissors.png",
        "hand_paper.png",
    ]

    for img_idx, filename in enumerate(filenames):
        img = pyxel.image(img_idx)
        img.load(0, 0, filename)

        # 左上の色を背景色とみなして透過処理
        bg_col = img.pget(0, 0)
        for y in range(HAND_ICON_SIZE):
            for x in range(HAND_ICON_SIZE):
                if img.pget(x, y) == bg_col:
                    img.pset(x, y, 0)  # 0 = 透明色


def draw_hand_icon(hand: int, x: int, y: int) -> None:
    """
    指定した手アイコンを (x, y) に描画する。
    今は 2倍(32x32)表示。
    (x, y) は左上座標。
    """
    img_idx = HAND_IMG_INDEX[hand]
    pyxel.blt(
        x,
        y,
        img_idx,
        0,
        0,
        HAND_ICON_SIZE,
        HAND_ICON_SIZE,
        0,
        2,
        2,  # 2倍表示
    )


# 画像読み込み
_load_hand_images()

# ===== シーン管理 =====
# 0: TITLE, 1: GAME, 2: HOW TO
scene = 0
last_scene = -1  # 直前のシーン (BGM切り替え用)

# ===== タイトルメニュー =====
menu_idx = 0  # 0: START, 1: HOW TO
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 52, 86, 56, 12),
]

# ===== GAME 用の状態管理 =====
# 0: Janken game begins!
# 1: Which hand should I play?
# 2: 手の選択
# 3: 1,2,3!
# 4: You win!
# 5: You lose...
# 6: Draw!
game_phase = 0
phase_timer = 0

player_hand = 0  # 0: ROCK, 1: SCISSORS, 2: PAPER
cpu_hand = 0

select_idx = 0  # ROCK / SCISSORS / PAPER 選択位置 (0,1,2)


# ===== 更新処理 =====
def update():
    global scene, last_scene

    if scene != last_scene:
        set_bgm_scene(scene)
        last_scene = scene

    if scene == 0:
        update_title()
    elif scene == 1:
        update_game()
    elif scene == 2:
        update_howto()


def update_title():
    global scene, menu_idx

    # 上下キーでメニュー選択
    if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
        if menu_idx > 0:
            menu_idx -= 1

    if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
        if menu_idx < len(MENU) - 1:
            menu_idx += 1

    # 決定
    if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(
        pyxel.GAMEPAD1_BUTTON_A
    ):
        if menu_idx == 0:
            start_game()
        elif menu_idx == 1:
            go_howto()


def start_game():
    global scene, game_phase, phase_timer, select_idx
    scene = 1
    game_phase = 1
    phase_timer = 0
    select_idx = 0


def go_howto():
    global scene
    scene = 2


def update_game():
    global game_phase, phase_timer
    global select_idx, player_hand, cpu_hand, scene

    phase_timer += 1

    # 手の選択フェーズ
    if game_phase == 1:
        # 左右で選択
        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            if select_idx > 0:
                select_idx -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            if select_idx < 2:
                select_idx += 1

        # 決定
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            player_hand = select_idx
            cpu_hand = random.randint(0, 2)
            game_phase = 3  # 3! のカウントダウン
            phase_timer = 0

    # 3! → 結果表示へ
    elif game_phase == 3:
        # 3! を少し見せてから結果へ
        if phase_timer > 45:  # 約1.5秒 (fps=30)
            # 勝敗判定
            if player_hand == cpu_hand:
                game_phase = 6  # Draw
            elif (player_hand - cpu_hand) % 3 == 1:
                game_phase = 4  # Win
            else:
                game_phase = 5  # Lose
            phase_timer = 0

    # 結果表示 → Z でタイトルへ戻る
    elif game_phase in (4, 5, 6):
        if (
            pyxel.btnp(pyxel.KEY_Z)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        ):
            scene = 0  # タイトルへ戻る


def update_howto():
    global scene
    # Z でタイトルに戻る
    if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
        scene = 0


# ===== 描画処理 =====
def draw():
    pyxel.cls(0)

    if scene == 0:
        draw_title()
    elif scene == 1:
        draw_game()
    elif scene == 2:
        draw_howto()


def draw_title():
    pyxel.cls(0)

    pyxel.text(54, 30, "JANKEN GAME", 7)

    for i, (label, x, y, w, h) in enumerate(MENU):
        # 枠
        col = 5 if i == menu_idx else 1
        pyxel.rectb(x, y, w, h, col)

        # テキスト中央寄せ
        text_w = len(label) * 4
        tx = x + (w - text_w) // 2
        ty = y + 3
        pyxel.text(tx, ty, label, 7)

    pyxel.text(32, 110, "Z / A: OK   UP/DOWN: MOVE", 6)


def draw_game():
    pyxel.cls(0)

    # 下のメッセージパネル
    panel_h = 28
    panel_y = SCREEN_H - panel_h
    pyxel.rect(0, panel_y, SCREEN_W, panel_h, 1)
    pyxel.rectb(0, panel_y, SCREEN_W, panel_h, 13)

    # メッセージ表示
    msg = ""
    if game_phase == 1:
        msg = "Which hand should I play?"
    elif game_phase == 3:
        msg = "3!"
    elif game_phase == 4:
        msg = "You win!"
    elif game_phase == 5:
        msg = "You lose..."
    elif game_phase == 6:
        msg = "Draw..."

    if msg:
        text_w = len(msg) * 4
        pyxel.text((SCREEN_W - text_w) // 2, panel_y + 10, msg, 7)

    # ===== 手の表示 =====
    center_x = SCREEN_W // 2 - HAND_ICON_SIZE  # 2倍(32px)の半分 = 16
    player_y = panel_y - HAND_ICON_SIZE * 2    # 枠のすぐ上
    cpu_y = player_y - HAND_ICON_SIZE * 2      # その上

    if game_phase == 1:
        # 手の選択中：枠のすぐ上に表示
        draw_hand_icon(select_idx, center_x, player_y)

        # 下に ROCK / SCISSORS / PAPER の選択肢
        labels = ["ROCK", "SCISSORS", "PAPER"]
        xs = [20, 58, 112]
        for i, label in enumerate(labels):
            col = 7 if i == select_idx else 5
            pyxel.text(xs[i], panel_y - 8, label, col)

    elif game_phase == 3:
        # ★ 3! のときだけ、画面の真ん中に自分と相手の手を表示 ★

        # 2倍表示(32x32)なので、完全中央に置くために 16 ずらす
        base_x = SCREEN_W // 2 - HAND_ICON_SIZE
        base_y = SCREEN_H // 2 - HAND_ICON_SIZE

        # 自分の手(上)、相手の手(下)を少しずらして縦に並べる
        draw_hand_icon(player_hand, base_x, base_y - 10)
        draw_hand_icon(cpu_hand, base_x, base_y + 10)

    elif game_phase in (4, 5, 6):
        # 結果表示中：両者の手を枠の上に表示
        draw_hand_icon(player_hand, center_x, player_y)
        draw_hand_icon(cpu_hand, center_x, cpu_y)


def draw_howto():
    pyxel.cls(0)
    pyxel.text(10, 20, "HOW TO PLAY", 7)
    pyxel.text(10, 40, "- Select ROCK / SCISSORS / PAPER", 7)
    pyxel.text(10, 52, "- Press Z / A to decide", 7)
    pyxel.text(10, 76, "Press Z / A to BACK", 6)


pyxel.run(update, draw)