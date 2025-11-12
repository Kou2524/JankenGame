import pyxel

pyxel.init(160, 120, title="じゃんけんゲーム")

def update():
    pass

def draw():
    pyxel.cls(0)
    # ここでのタイトル文字描画はやめて、HTML側で日本語を表示
    pyxel.text(30, 80, "PRESS ANY KEY...", 13)

pyxel.run(update, draw)