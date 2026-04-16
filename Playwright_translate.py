# -*- coding: UTF-8 -*-
# 2026/4/16 00:02
import logging
import signal
import sys
from multiprocessing import Queue

from playwright.sync_api import sync_playwright

from enmu_data import ele_selector
from logger import Logger

# 多进程中使用独立的 logger，避免 handler 重复添加
logging.basicConfig(level=logging.DEBUG)
logger = Logger(f"./logs/{__name__}.log", log_name=__name__).logger


class Playwright_translate:
    def __init__(self, queue: Queue):
        # 谷歌翻译地址
        self.url = "https://google-translate-proxy.tantu.com/"
        # self.url = "https://translate.google.com/"

        # 进程队列
        self.queue = queue

        # 当前正在执行的任务标识
        self.current_task = None

        # 注册信号处理器，用于安全终止
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.run_playwright_process()

    def connect_windows(self):
        """连接并控制 pywebview 窗口"""
        logger.debug("创建 Playwright 实例")
        # 创建 Playwright 实例
        self.PlaywrightContextManager = sync_playwright().start()

        logger.debug("触发连接webview")

        # 连接到本地调试端口
        self.Browser = self.PlaywrightContextManager.chromium.connect_over_cdp("http://localhost:9222")
        logger.debug("连接到本地调试端口--http://localhost:9222")

        # 获取第一个浏览器上下文和页面
        self.context = self.Browser.contexts[0]
        logger.debug("获取第一个浏览器上下文和页面")

        self.page = self.context.pages[0]
        logger.debug("获取页面实例")

        # 导航到url
        self.page.goto(self.url)
        logger.debug(f"导航到url--{self.url}")

    def _signal_handler(self, signum, frame):
        """
        信号处理器 - 安全终止进程
        """
        logger.warning(f"收到终止信号: {signum}")
        self._cleanup()
        sys.exit(0)

    def _cleanup(self):
        """
        清理资源
        """
        logger.debug("清理 Playwright 资源...")
        if hasattr(self, 'page') and self.page:
            try:
                self.page.close()
            except:
                pass

        if hasattr(self, 'context') and self.context:
            try:
                self.context.close()
            except:
                pass

        if hasattr(self, 'Browser') and self.Browser:
            try:
                self.Browser.close()
            except:
                pass

        if hasattr(self, 'PlaywrightContextManager') and self.PlaywrightContextManager:
            try:
                self.PlaywrightContextManager.stop()
            except:
                pass

        logger.debug("资源清理完成")

    def run_playwright_process(self):
        """
        队列获取：p_task 对象或 {"func": "", "args": "[]", "kwargs": "{}"}
        """
        while True:
            task = self.queue.get()

            if task.func == "exit":
                logger.debug("收到退出信号，清理资源")
                self._cleanup()
                break

            # p_task 对象
            func_name = task.func
            args = task.args if isinstance(task.args, (list, tuple)) else ()
            kwargs = task.kwargs if isinstance(task.kwargs, dict) else {}

            # 记录当前任务
            self.current_task = func_name
            logger.debug(f"开始执行任务: {func_name}")

            # 反射调用
            try:
                method = getattr(self, func_name)  # 拿到方法
                method(*args, **kwargs)  # 执行
                logger.debug(f"任务完成: {func_name}")
            except Exception as e:
                logger.error(f"任务执行错误 [{func_name}]:", exc_info=True)
            finally:
                self.current_task = None

    def cancel_all_tasks(self):
        """
        清空队列中的所有待执行任务
        注意：无法中断正在执行的任务，只能等待其完成
        """
        cleared_count = 0
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                cleared_count += 1
            except Exception:
                break

        logger.debug(f"已取消 {cleared_count} 个待执行任务")
        return cleared_count

    def text_translation(self):
        """
        文本翻译
        """
        char_btn = self.page.locator(ele_selector.char_btn)
        claer_char_btn = self.page.locator(ele_selector.claer_char_btn)
        input_char_btn = self.page.locator(ele_selector.input_char_btn)

        char_btn.click()
        logger.debug("点击文字按钮")

        if claer_char_btn.is_visible():
            claer_char_btn.click()
            logger.debug("点击清空按钮")

        input_char_btn.click()
        logger.debug("点击输入框")
        self.page.keyboard.press("Control+v")
        logger.debug("粘贴文本")

    def img_translation(self):
        """
        图片翻译
        """
        img_btn = self.page.locator(ele_selector.img_btn)
        claer_img_btn = self.page.locator(ele_selector.claer_img_btn)

        img_btn.click()
        logger.debug("点击图片按钮")

        if claer_img_btn.is_visible():
            claer_img_btn.click()
            logger.debug("点击清空按钮")

        self.page.keyboard.press("Control+v")
