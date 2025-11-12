import pyxel

# 画面は160x120
pyxel.init(160, 120, title="Janken Game", fps=30)
pyxel.mouse(False)  # ← 十字カーソル非表示、座標はそのまま取得可能

# ----- state -----
scene = 0           # 0: タイトル / 1: ゲーム
menu_idx = 0        # キーボード用選択位置（0..n-1）

# メニュー項目（表示テキスト, x, y, w, h）
MENU = [
    ("START", 52, 70, 56, 12),
    ("HOW TO", 48, 86, 64, 12),
]

def tap_pressed():
    # Webでも確実な決定キー群
    return pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_Z)

def is_hover(mx, my, x, y, w, h):
    return (x <= mx < x + w) and (y <= my < y + h)

def update_title():
    global scene, menu_idx
    mx, my = pyxel.mouse_x, pyxel.mouse_y

    # ホバーでハイライト
    for i, (_, x, y, w, h) in enumerate(MENU):
        if is_hover(mx, my, x, y, w, h):
            menu_idx = i

    # キーボード操作（↑↓）
    if pyxel.btnp(pyxel.KEY_UP):
        menu_idx = (menu_idx - 1) % len(MENU)
    if pyxel.btnp(pyxel.KEY_DOWN):
        menu_idx = (menu_idx + 1) % len(MENU)

    # 決定（スペース/Enter/Z）
    if tap_pressed():
        if menu_idx == 0:      # START
            scene = 1
        elif menu_idx == 1:    # HOW TO（今回はトースト表示だけ）
            pyxel.play(0, 0)   # 効果音代わり。未設定なら無音

def update_game():
    global scene
    # ゲーム中はスペース/Enterでタイトルへ戻る（仮）
    if tap_pressed():
        scene = 0

def update():
    if scene == 0:
        update_title()
    else:
        update_game()

def draw_cursor(mx, my):
    # ちっちゃい十字カーソル（見た目用）
    # 画面外のときは描かない（初期値0,0暴発防止したいなら調整しよ）
    pyxel.line(mx - 3, my, mx + 3, my, 7)
    pyxel.line(mx, my - 3, mx, my + 3, 7)

def draw_title():
    pyxel.cls(0)
    pyxel.text(40, 45, "JANKEN GAME", 7)

    # メニュー描画
    for i, (label, x, y, w, h) in enumerate(MENU):
        hover = (i == menu_idx)
        # 枠
        col = 10 if hover else 5
        pyxel.rectb(x, y, w, h, col)
        # 中央寄せテキスト
        tx = x + (w - len(label) * 4) // 2
        ty = y + 3
        pyxel.text(tx, ty, label, 7 if hover else 6)

    # ヒント
    pyxel.text(18, 110, "Hover and press SPACE/ENTER", 13)

    # 自前カーソル
    draw_cursor(pyxel.mouse_x, pyxel.mouse_y)

def draw_game():
    pyxel.cls(1)
    pyxel.text(50, 58, "GAME START!", 7)
    pyxel.text(22, 100, "Press SPACE/ENTER to back", 11)
    draw_cursor(pyxel.mouse_x, pyxel.mouse_y)

def draw():
    if scene == 0:
        draw_title()
    else:
        draw_game()

pyxel.run(update, draw)