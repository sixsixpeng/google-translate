# -*- coding: UTF-8 -*-
# 2026/4/16 00:02


from playwright.sync_api import sync_playwright
from logger import Loger

logger = Loger().logger


class Playwright_translate:
    def __init__(self):
        # 谷歌翻译地址
        self.url = "https://google-translate-proxy.tantu.com/"
        # self.url = "https://translate.google.com/"





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


