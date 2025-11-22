import pyxel

# ゲーム画面を大きく表示（後で調整OK）
pyxel.init(160, 120, title="Janken Game", fps=30, display_scale=4)

# 青いカーソルを消す
pyxel.mouse(False)

# ===== シーン管理 =====
scene = 0          # 0: TITLE, 1: GAME, 2: HOW TO
menu_idx = 0       # START / HOW TO の選択位置


# ===== メニューの配置 =====
MENU = [
    ("START", 48, 70, 64, 12),
    ("HOW TO", 48, 86, 64, 12),
]


# ===== 十字キーの中心座標 =====
pad_cx = pyxel.width // 2
pad_cy = pyxel.height - 25
pad_size = 12   # ボタンの1辺のサイズ


# ======= 中央文字表示 =======
def draw_centered_text(y, text, col):
    text_w = len(text) * 4
    x = (pyxel.width - text_w) // 2
    pyxel.text(x, y, text, col)


# ======= 十字キーの描画 =======
def draw_dpad():
    col = 12  # 明るい青

    # 上
    pyxel.rect(pad_cx - pad_size//2, pad_cy - pad_size*2, pad_size, pad_size, col)
    # 下
    pyxel.rect(pad_cx - pad_size//2, pad_cy + pad_size, pad_size, pad_size, col)
    # 左
    pyxel.rect(pad_cx - pad_size*2, pad_cy - pad_size//2, pad_size, pad_size, col)
    # 右
    pyxel.rect(pad_cx + pad_size, pad_cy - pad_size//2, pad_size, pad_size, col)


# ======= 十字キーの入力判定 =======
def dpad_input():
    mx, my = pyxel.mouse_x, pyxel.mouse_y

    if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):

        # 上
        if (pad_cx - pad_size//2 <= mx <= pad_cx + pad_size//2 and
            pad_cy - pad_size*2 <= my <= pad_cy - pad_size):
            return "up"

        # 下
        if (pad_cx - pad_size//2 <= mx <= pad_cx + pad_size//2 and
            pad_cy + pad_size <= my <= pad_cy + pad_size*2):
            return "down"

        # 左
        if (pad_cx - pad_size*2 <= mx <= pad_cx - pad_size and
            pad_cy - pad_size//2 <= my <= pad_cy + pad_size//2):
            return "left"

        # 右
        if (pad_cx + pad_size <= mx <= pad_cx + pad_size*2 and
            pad_cy - pad_size//2 <= my <= pad_cy + pad_size//2):
            return "right"

    return None


# ======= UPDATE =======
player_x = 80
player_y = 60


def update():
    global scene, menu_idx
    global player_x, player_y

    if scene == 0:
        # ===== タイトル =====

        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # キー選択
        if pyxel.btnp(pyxel.KEY_UP):
            menu_idx = (menu_idx - 1) % len(MENU)
        if pyxel.btnp(pyxel.KEY_DOWN):
            menu_idx = (menu_idx + 1) % len(MENU)

        # 決定
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            scene = 1 if menu_idx == 0 else 2

        # タップ判定（ゆるくY判断）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if 70 <= my < 82:
                scene = 1
            elif 86 <= my < 98:
                scene = 2

    elif scene == 1:
        # ===== ゲーム画面 =====

        # 十字キーの入力
        d = dpad_input()

        if d == "up":
            player_y -= 1
        elif d == "down":
            player_y += 1
        elif d == "left":
            player_x -= 1
        elif d == "right":
            player_x += 1

        # PC操作（矢印キーでも動かす）
        if pyxel.btn(pyxel.KEY_UP):
            player_y -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            player_y += 1
        if pyxel.btn(pyxel.KEY_LEFT):
            player_x -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            player_x += 1

        # タイトルに戻る
        if (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            and my < 30  # 画面上部タップで戻る
        ):
            scene = 0

    elif scene == 2:
        # ===== HOW TO =====
        if (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        ):
            scene = 0


# ======= DRAW =======
def draw():
    pyxel.cls(0)

    if scene == 0:
        # ===== タイトル画面 =====
        draw_centered_text(30, "JANKEN GAME", 7)

        for i, (label, x, y, w, h) in enumerate(MENU):
            hi = i == menu_idx

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

        draw_centered_text(110, "ARROW + ENTER / CLICK", 13)

    elif scene == 1:
        # ===== ゲーム画面 =====
        pyxel.cls(1)

        # プレイヤーキャラ
        pyxel.circ(player_x, player_y, 4, 8)

        # 十字キー
        draw_dpad()

        draw_centered_text(5, "GAME SCREEN", 7)

    elif scene == 2:
        # ===== HOW TO =====
        draw_centered_text(20, "HOW TO PLAY", 10)
        pyxel.text(10, 50, "- Use DPAD or keys", 7)
        pyxel.text(10, 60, "- Move player", 7)
        pyxel.text(10, 80, "Press SPACE/CLICK to TITLE", 13)


pyxel.run(update, draw)