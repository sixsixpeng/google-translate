# -*- coding: UTF-8 -*-
# 2026/4/12 15:33
import webview
import time
from logger import Logger
from Playwright_translate import Playwright_translate
from Hotkey import HotkeyListener
from multiprocessing import Queue as process_queue, Process
from threading import Thread
from enmu_data import p_task

logger = Logger(f"./logs/{__name__}.log",log_name=__name__).logger

# 设置远程调试端口
webview.settings['REMOTE_DEBUGGING_PORT'] = 9222
logger.debug(f"设置远程调试端口:{webview.settings['REMOTE_DEBUGGING_PORT']}")


class App:
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

        self.PROCESS_TASK_LIST = process_queue()
        self.playwright_process = None

        # 使用 closing 事件（窗口关闭前触发）
        self.window.events.closing += self.on_closing
        logger.debug("设置closing事件回调")

        # 键盘监听
        logger.debug("启动键盘监听")
        Thread(target=HotkeyListener, args=(self.PROCESS_TASK_LIST,), daemon=True).start()

        # 开启循环，这句放到最后
        self.start_windows()

    def on_closing(self):
        """
        窗口即将关闭时的清理工作
        """
        logger.debug("窗口即将关闭，开始清理资源")

        # 取消所有待执行任务
        self.PROCESS_TASK_LIST.put(p_task("cancel_all_tasks"))

        # 发送退出信号
        self.PROCESS_TASK_LIST.put("exit")

        # 等待进程结束
        if self.playwright_process and self.playwright_process.is_alive():
            logger.debug("等待 Playwright 进程退出...")
            self.playwright_process.join(timeout=1)
            if self.playwright_process.is_alive():
                logger.info("Playwright 进程未在规定时间内退出，强制终止")
                self.playwright_process.kill()

        logger.debug("资源清理完成")
        return None  # 返回 None 避免 pywebview 事件系统错误

    def start_windows(self):
        logger.debug("启动窗口")
        webview.start(self.connect_windows,  # 窗口初始化完成回调
                      debug=False,
                      private_mode=False,
                      storage_path=f'./cache/'
                      )

    def connect_windows(self):
        self.playwright_process = Process(target=Playwright_translate, args=(self.PROCESS_TASK_LIST,))
        self.playwright_process.start()
        logger.debug(f"Playwright 进程已启动，PID: {self.playwright_process.pid}")

        self.PROCESS_TASK_LIST.put(p_task("connect_windows"))


if __name__ == '__main__':
    win = App()
