import pyxel

pyxel.init(160, 120, title="Janken Game", fps=30)

# 0: TITLE / 1: GAME
scene = 0
menu_idx = 0  # 選択中の項目（今は1個だけ）

# (表示名, x, y, w, h)
# HOW TO を削除して、START だけにする
MENU = [
    ("START", 52, 72, 56, 12),  # ← JANKEN と 説明文のちょうど真ん中あたり
]

def btn_decide():
    return pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN)

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
        # マウス位置でホバー反映（今はSTARTだけだけど一応そのまま）
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        for i, (_, x, y, w, h) in enumerate(MENU):
            if in_rect(mx, my, x, y, w, h):
                menu_idx = i

        # ↑↓で移動（1個しかないので実質 menu_idx は0のまま）
        if pyxel.btnp(pyxel.KEY_UP):
            menu_idx = (menu_idx - 1) % len(MENU)
        if pyxel.btnp(pyxel.KEY_DOWN):
            menu_idx = (menu_idx + 1) % len(MENU)

        # 決定
        if btn_decide():
            scene = 1  # STARTしかないので、押したらGAMEへ

    else:
        # ゲーム中は決定キーでタイトルへ戻る（仮）
        if btn_decide():
            scene = 0

def draw():
    pyxel.cls(0)

    if scene == 0:
        # タイトルを中央に
        draw_centered_text(45, "JANKEN GAME", 7)

        # START ボタン
        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = (i == menu_idx)
            pyxel.rectb(x, y, w, h, 10 if hi else 5)
            tx = x + (w - len(label) * 4) // 2
            pyxel.text(tx, y + 3, label, 7 if hi else 6)

        # 説明文も中央に
        draw_centered_text(110, "Hover and press SPACE/ENTER", 13)

    else:
        pyxel.cls(1)
        draw_centered_text(58, "GAME START!", 7)
        draw_centered_text(100, "Press SPACE/ENTER to back", 11)

pyxel.run(update, draw)