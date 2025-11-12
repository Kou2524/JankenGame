import pyxel

# 画面状態: 0 = タイトル, 1 = ゲーム画面
scene = 0

def update():
    global scene
    # クリックまたはキー入力で切り替え
    if scene == 0:
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            scene = 1

def draw():
    pyxel.cls(0)
    if scene == 0:
        # タイトル画面
        pyxel.text(40, 50, "JANKEN GAME", 7)
        pyxel.text(66, 80, "START", 10)
        pyxel.text(30, 100, "CLICK OR PRESS SPACE", 13)
    elif scene == 1:
        # ゲーム画面（仮）
        pyxel.text(50, 60, "GAME START!", 11)
        pyxel.text(30, 90, "Tap to return", 5)
        # タップでタイトルに戻る（開発用）
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            scene = 0

pyxel.init(160, 120, title="Janken Game", fps=30)
pyxel.mouse(True)  # ←マウスカーソルON
pyxel.run(update, draw)