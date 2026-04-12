# -*- coding: UTF-8 -*-
# 2026/4/12 15:33

# pyinstaller -D -w -i icon.ico m3.py
import webview

# 创建窗口
window = webview.create_window(
    title="事件演示窗口",
    url="https://google-translate-proxy.tantu.com/",
    width=800,
    height=500,
    on_top=True,
    text_select=True,
    zoomable=True,
    min_size=(600, 500),
)

webview.start(debug=False,
              private_mode=False,
              storage_path=f'./cache/'
              )
