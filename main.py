import pyxel

pyxel.init(160, 120, title="Janken Game")

# じゃんけん画像を後で使いたい場合はここで pyxel.load("assets.pyxres") とかにできる
# 今はテキストだけの仮タイトル画面

def update():
    pass

def draw():
    pyxel.cls(0)
    pyxel.text(40, 50, "JANKEN GAME", 7)
    pyxel.text(30, 80, "PRESS ANY KEY...", 13)

pyxel.run(update, draw)