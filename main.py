import pyxel

WIDTH = 160
HEIGHT = 120

pyxel.init(WIDTH, HEIGHT, title="Janken Game", fps=30)
pyxel.mouse(False)

# 0: TITLE / 1: GAME
scene = 0

# ===== タイトル用 =====
menu_idx = 0  # 0: START

# ===== GAME用 =====
DIALOG_Y = 80
DIALOG_H = 40

HAND_NAMES = ["グー", "チョキ", "パー"]
hand_idx = 0  # プレイヤーが選んでいる手のインデックス
dialog_text = "レゼ「どの手を出す？」"

def update():
    global scene
    if scene == 0:
        update_title()
    elif scene == 1:
        update_game()


# =========================
#   TITLE
# =========================
def update_title():
    global scene, menu_idx

    # 上下でメニュー移動（今は項目1個だけだけど形だけ）
    if pyxel.btnp(pyxel.KEY_UP):
        menu_idx = max(0, menu_idx - 1)
    if pyxel.btnp(pyxel.KEY_DOWN):
        menu_idx = min(0, menu_idx + 1)

    # Z / ENTER で決定
    if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
        if menu_idx == 0:  # START
            scene = 1


def draw_title():
    pyxel.cls(0)

    title = "JANKEN GAME"
    x = (WIDTH - len(title) * 4) // 2
    pyxel.text(x, 40, title, 7)

    # START ボタン風
    text = "START"
    w = len(text) * 4 + 8
    h = 14
    bx = (WIDTH - w) // 2
    by = 70

    # 枠
    pyxel.rect(bx, by, w, h, 1)
    pyxel.rectb(bx, by, w, h, 7)

    # 文字
    tx = bx + 4
    ty = by + 4
    pyxel.text(tx, ty, text, 7)

    # カーソル（▷）
    pyxel.text(bx - 10, ty, "▷" if menu_idx == 0 else "  ", 10)


# =========================
#   GAME
# =========================
def update_game():
    global hand_idx, dialog_text

    # ←→ で手を変更
    if pyxel.btnp(pyxel.KEY_LEFT):
        hand_idx = (hand_idx - 1) % len(HAND_NAMES)
    if pyxel.btnp(pyxel.KEY_RIGHT):
        hand_idx = (hand_idx + 1) % len(HAND_NAMES)

    # Z / ENTER で決定（とりあえずセリフだけ変える）
    if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
        chosen = HAND_NAMES[hand_idx]
        dialog_text = f"レゼ「{chosen} なんだ？」"


def draw_game():
    pyxel.cls(0)

    # --- 上のバトルエリア（とりあえず適当に絵を置くゾーン） ---
    pyxel.text(10, 10, "ENEMY", 8)
    pyxel.text(10, 30, "YOU", 11)

    # ここにそのうち、グー・チョキ・パーのアイコン出したり、キャラ絵出したりできる

    # --- 下のセリフ枠 ---
    draw_dialog_window()


def draw_dialog_window():
    # ウィンドウの背景
    pyxel.rect(0, DIALOG_Y, WIDTH, DIALOG_H, 1)      # 中身
    pyxel.rectb(0, DIALOG_Y, WIDTH, DIALOG_H, 7)     # 枠線

    # セリフ（1行目）
    pyxel.text(4, DIALOG_Y + 4, dialog_text, 7)

    # 選択肢（2行目）
    # [グー]  チョキ  パー みたいな感じで中央寄せ
    options_text = ""
    for i, name in enumerate(HAND_NAMES):
        if i == hand_idx:
            # 選択中は [ ] で囲む
            options_text += f"[{name}] "
        else:
            options_text += f" {name}  "

    text_w = len(options_text) * 4
    ox = (WIDTH - text_w) // 2
    oy = DIALOG_Y + 16
    pyxel.text(ox, oy, options_text, 7)

    # カーソル（選択中の手の下に▼）
    # とりあえずざっくり位置合わせ（雑でも雰囲気は出る）
    cursor_x = ox + hand_idx * 4 * 4  # 文字幅4×(ざっくり4文字ぶん)くらいでずらす
    cursor_y = oy + 8
    pyxel.text(cursor_x, cursor_y, "▼", 10)


def draw():
    if scene == 0:
        draw_title()
    elif scene == 1:
        draw_game()


pyxel.run(update, draw)
