import pyxel

# ==== JS側のBGM切り替え（あれば） =================================
try:
    from js import set_bgm_scene as _set_bgm_scene_js

    def set_bgm_scene(scene: int) -> None:
        _set_bgm_scene_js(scene)

except ImportError:
    # ローカル実行用のダミー
    def set_bgm_scene(scene: int) -> None:
        pass


# ==== 定数 ==========================================================
WIDTH = 160
HEIGHT = 120

SCENE_TITLE = 0
SCENE_GAME = 1

# セリフウィンドウ用
DIALOG_Y = 80
DIALOG_H = 40

HAND_NAMES = ["グー", "チョキ", "パー"]

# ==== 状態 ==========================================================
scene = SCENE_TITLE
menu_idx = 0  # いまはSTARTしかないけど一応
hand_idx = 0  # プレイヤーが選んでる手
dialog_text = "レゼ「どの手を出す？」"

# ==== 初期化 ========================================================
pyxel.init(WIDTH, HEIGHT, title="Janken Game", fps=30)
pyxel.mouse(False)


# ==== 共通の小物 ====================================================
def draw_centered_text(y: int, text: str, col: int) -> None:
    text_w = len(text) * 4
    x = (WIDTH - text_w) // 2
    pyxel.text(x, y, text, col)


# ==== メインループ ==================================================
def update():
    global scene

    if scene == SCENE_TITLE:
        update_title()
    elif scene == SCENE_GAME:
        update_game()


def draw():
    pyxel.cls(0)

    if scene == SCENE_TITLE:
        draw_title()
    elif scene == SCENE_GAME:
        draw_game()


# ==== TITLEシーン ===================================================
def update_title():
    global scene

    # STARTボタンを押したらGAMEへ
    # キーボード or 仮想ゲームパッドのZ / ENTER / SPACE
    if (
        pyxel.btnp(pyxel.KEY_Z)
        or pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
    ):
        scene = SCENE_GAME
        set_bgm_scene(1)

    # マウスクリックでもOK（PC用）
    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        bx, by, bw, bh = 52, 70, 56, 12
        if bx <= mx < bx + bw and by <= my < by + bh:
            scene = SCENE_GAME
            set_bgm_scene(1)


def draw_title():
    # タイトル
    draw_centered_text(40, "JANKEN GAME", 7)

    # STARTボタン風
    text = "START"
    w = len(text) * 4 + 8
    h = 14
    bx = (WIDTH - w) // 2
    by = 70

    pyxel.rect(bx, by, w, h, 1)     # 中
    pyxel.rectb(bx, by, w, h, 7)    # 枠
    pyxel.text(bx + 4, by + 4, text, 7)


# ==== GAMEシーン ====================================================
def update_game():
    global hand_idx, dialog_text

    # ←→で手を選ぶ
    if pyxel.btnp(pyxel.KEY_LEFT):
        hand_idx = (hand_idx - 1) % len(HAND_NAMES)
    if pyxel.btnp(pyxel.KEY_RIGHT):
        hand_idx = (hand_idx + 1) % len(HAND_NAMES)

    # 決定（Z / ENTER / SPACE）
    if (
        pyxel.btnp(pyxel.KEY_Z)
        or pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.KEY_SPACE)
    ):
        chosen = HAND_NAMES[hand_idx]
        dialog_text = f"レゼ「{chosen} なんだ？」"


def draw_game():
    # --- 上のバトルエリア（そのうち手とかキャラ絵を置くゾーン） ---
    pyxel.text(10, 10, "ENEMY", 8)
    pyxel.text(10, 30, "YOU", 11)
    draw_centered_text(20, "VS", 7)

    # --- 下のセリフウィンドウ ---
    # 背景
    pyxel.rect(0, DIALOG_Y, WIDTH, DIALOG_H, 1)
    pyxel.rectb(0, DIALOG_Y, WIDTH, DIALOG_H, 7)

    # セリフ
    pyxel.text(4, DIALOG_Y + 4, dialog_text, 7)

    # 選択肢表示
    options_text = ""
    for i, name in enumerate(HAND_NAMES):
        if i == hand_idx:
            options_text += f"[{name}] "
        else:
            options_text += f" {name}  "

    text_w = len(options_text) * 4
    ox = (WIDTH - text_w) // 2
    oy = DIALOG_Y + 16
    pyxel.text(ox, oy, options_text, 7)

    # カーソル（だいたいの位置で▼）
    cursor_x = ox + hand_idx * 4 * 4  # ざっくり4文字分ずつずらす
    cursor_y = oy + 8
    pyxel.text(cursor_x, cursor_y, "▼", 10)


pyxel.run(update, draw)