# -*- coding: UTF-8 -*-
# 2026/4/15 23:30


import logging
from pathlib import Path
import sys
from datetime import datetime
from logging import handlers



class ColoredFormatter(logging.Formatter):
    # 颜色方案
    COLORS = {
        logging.DEBUG: '\033[96m',  # 亮青色，加粗
        logging.INFO: '\033[92m',  # 亮绿色，加粗
        logging.WARNING: '\033[93;1m',  # 亮黄色，加粗
        logging.ERROR: '\033[91;1;5m',  # 亮红色，加粗，闪烁
        logging.CRITICAL: '\033[97;101;1;5m',  # 亮白色文本，亮红色背景，加粗，闪烁
    }
    RESET = '\033[0m'  # 重置颜色

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)

    def formatTime(self, record, datefmt=None):
        # 使用 datetime 模块自定义时间格式
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return super().formatTime(record, datefmt)

    def format(self, record):
        # 添加颜色
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


class Loger:
    def __init__(self, log_path="./logs/translate.log"):
        self.log_path = log_path

        # 输出控制台和文件最低日志级别
        self.FileHandler_log_level = logging.DEBUG
        self.StreamHandler_log_level = logging.DEBUG

        # 初始化日志路径
        self.check_directory(self.log_path)

        # 配置日志
        self.configure_handlers()

    def check_directory(self,check_path):
        """
        确保路径存在，如果不存在则创建（包括多级目录）。
        :param check_path: 相对或绝对路径
        """
        check_path = Path(check_path)
        check_path.parent.mkdir(parents=True, exist_ok=True)


    def configure_handlers(self):
        # 配置日志
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的 handler，避免重复添加
        self.logger.handlers.clear()

        # 定义日志格式和时间格式
        color_formatter = ColoredFormatter(fmt='%(asctime)s | %(levelname)s| %(module)s.%(funcName)s:%(lineno)d | processID:%(process)d | thread_ID:%(thread)d | %(message)s',
                                           datefmt='%Y/%m/%d %H:%M:%S.%f')  # 自定义时间格式，包含微秒
        text_formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s| %(module)s.%(funcName)s:%(lineno)d | processID:%(process)d | thread_ID:%(thread)d | %(message)s',
                                           datefmt='%Y/%m/%d %H:%M:%S')  # 自定义时间格式，包含微秒

        # 输出到控制台
        handler_Stream = logging.StreamHandler(sys.stdout)  # 控制台
        handler_Stream.setFormatter(color_formatter)
        handler_Stream.setLevel(self.StreamHandler_log_level)
        self.logger.addHandler(handler_Stream)

        # 输出到文件按照时间分割
        handler_TimedRotatingFile = handlers.TimedRotatingFileHandler(self.log_path,
                                                                      when='midnight',  # 每天午夜轮转
                                                                      interval=1,  # 每天轮转一次
                                                                      backupCount=7,  # 保留 7 个备份文件
                                                                      encoding='utf-8',
                                                                      delay=True)  # 延迟直到需要才单开
        handler_TimedRotatingFile.setFormatter(text_formatter)
        handler_TimedRotatingFile.setLevel(logging.DEBUG)
        self.logger.addHandler(handler_TimedRotatingFile)

    def demo_business(self):
        # 测试日志输出
        self.logger.debug('This is a debug message')
        self.logger.info('This is an info message')
        self.logger.warning('This is a warning message')
        self.logger.error('This is an error message')
        self.logger.critical('This is a critical message')
        self.logger.exception('This is a exception message')



if __name__ == '__main__':
    loger = Loger()
    loger.demo_business()
