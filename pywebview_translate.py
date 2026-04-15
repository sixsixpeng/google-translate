# -*- coding: UTF-8 -*-
# 2026/4/12 15:33

# pyinstaller -D -w -i icon.ico m3.py
import webview
import time
from logger import Loger
from Playwright_translate import Playwright_translate
from run_task import kill_all_process

logger = Loger().logger

# 设置远程调试端口
webview.settings['REMOTE_DEBUGGING_PORT'] = 9222
logger.debug(f"设置远程调试端口:{webview.settings['REMOTE_DEBUGGING_PORT']}")


class App(Playwright_translate):
    def __init__(self):
        # 创建窗口
        super().__init__()
        self.window = webview.create_window(
            title="事件演示窗口",
            url="",
            width=800,
            height=500,
            on_top=True,
            text_select=True,
            zoomable=True,
            min_size=(600, 500),
        )
        logger.debug("创建窗口实例")

        self.PROCESS_TASK_LIST = list()
        self.THREAD_TASK_LIST = list()

        self.window.events.closed += lambda: kill_all_process(self.PROCESS_TASK_LIST, self.THREAD_TASK_LIST)
        logger.debug("设置closed事件回调")

        # 开启循环，这句放到最后
        self.start_windows()

    def start_windows(self):
        logger.debug("启动窗口")
        webview.start(self.connect_windows,  # 窗口初始化完成回调
                      debug=False,
                      private_mode=False,
                      storage_path=f'./cache/'
                      )


if __name__ == '__main__':
    win = App()
