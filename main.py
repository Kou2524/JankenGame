elif game_phase == 9:
    # YES / NO 選択（枠を広げて収める）

    # 枠の開始位置と高さを再定義（下パネルを広めに）
    panel_h = 32
    panel_y = SCREEN_H - panel_h

    # 下パネル描き直し
    pyxel.rect(0, panel_y, SCREEN_W, panel_h, 1)
    pyxel.rectb(0, panel_y, SCREEN_W, panel_h, 7)

    msg_y = panel_y + 6

    # Continue
    draw_centered_text(msg_y, "Continue?", 7)

    # YES / NO
    labels = ["YES", "NO"]
    slot_w = 45
    start_x = (SCREEN_W - slot_w * 2) // 2

    for i, label in enumerate(labels):
        x = start_x + i * slot_w
        text_x = x + (slot_w - len(label) * 4) // 2
        pyxel.text(text_x, msg_y + 12, label, 7)

        # 点滅カーソル
        if i == continue_cursor and pyxel.frame_count % 20 < 10:
            tri_x = text_x - 6
            tri_y1 = msg_y + 11
            tri_y2 = msg_y + 19
            tri_m = (tri_y1 + tri_y2) // 2
            pyxel.tri(tri_x + 4, tri_m, tri_x, tri_y1, tri_x, tri_y2, 7)
