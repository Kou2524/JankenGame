import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)

# 0: TITLE / 1: GAME
scene = 0
# ★ 初期は「未選択」にしておく
menu_idx = -1  # 何も選ばれてない状態

# (表示名, x, y, w, h)
MENU = [
    ("START", 52, 72, 56, 12),
]

def btn_decide():
    # ★ SPACE / ENTER に加えて マウス左クリック でも決定できるように
    return (
        pyxel.btnp(pyxel.KEY_SPACE)
        or pyxel.btnp(pyxel.KEY_RETURN)
        or pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON)
    )

def in_rect(mx, my, x, y, w, h):
    return x <= mx < x + w and y <= my < y + h

# 横方向の中央にテキストを出す関数
def draw_centered_text(y, text, col):
    text_w = len(text) * 4          # フォント幅4px × 文字数
    x = (pyxel.width - text_w) // 2 # 画面幅から逆算して中央
    pyxel.text(x, y, text, col)

def update():
    global scene, menu_idx

    if scene == 0:
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # ★ マウスがボタンの上に来たら menu_idx を更新
        for i, (_, x, y, w, h) in enumerate(MENU):
            if in_rect(mx, my, x, y, w, h):
                menu_idx = i

        # ★ ↑↓キーでも選択できるように
        if pyxel.btnp(pyxel.KEY_UP):
            if menu_idx == -1:
                menu_idx = 0
            else:
                menu_idx = (menu_idx - 1) % len(MENU)

        if pyxel.btnp(pyxel.KEY_DOWN):
            if menu_idx == -1:
                menu_idx = 0
            else:
                menu_idx = (menu_idx + 1) % len(MENU)

        # ★ 何かが選ばれている状態で決定ボタンが押されたらゲームへ
        if menu_idx != -1 and btn_decide():
            scene = 1

    else:
        # ゲーム中は決定キーでタイトルへ戻る（仮）
        if btn_decide():
            scene = 0

def draw():
    pyxel.cls(0)

    if scene == 0:
        # タイトルを中央に
        draw_centered_text(45, "JANKEN GAME", 7)

        # START ボタン（選ばれてるときだけ黄色枠）
        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)              # 選択中かどうか
            border_col = 10 if hi else 5      # ★ 選択中：黄色 / 非選択：青
            text_col = 7 if hi else 6

            pyxel.rectb(x, y, w, h, border_col)
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, text_col)

        # 説明文も中央に
        draw_centered_text(110, "Hover and press SPACE/ENTER", 13)

    else:
        pyxel.cls(1)
        draw_centered_text(58, "GAME START!", 7)
        draw_centered_text(100, "Press SPACE/ENTER to back", 11)

pyxel.run(update, draw)