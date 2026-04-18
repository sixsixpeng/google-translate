# -*- coding: UTF-8 -*-
# 2026/4/15 23:30


import logging
import sys
from datetime import datetime
from logging import handlers
from pathlib import Path


def get_app_path():
    """获取可执行文件所在目录（兼容开发环境和打包环境）"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        return str(Path(sys.executable).parent)
    else:
        # 开发环境
        return str(Path(__file__).parent)


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


class Logger:
    def __init__(self, save_path,
                 log_level=logging.DEBUG,
                 StreamHandler_log_level=logging.DEBUG,
                 FileHandler_log_level=logging.DEBUG,
                 log_name=None):
        """
        初始化日志配置类

        :param save_path: 日志保存路径，例"./logs/xxx.log"
        :param log_level: 记录器(Logger)的全局日志级别，控制整个记录器的最低输出级别
        :param StreamHandler_log_level: 控制台处理器(StreamHandler)的日志级别，独立控制控制台输出的最低级别
        :param FileHandler_log_level: 文件处理器(FileHandler)的日志级别，独立控制文件输出的最低级别
        :param log_name: 具有指定名称的记录器，并在必要时创建它。如果未指定名称，则使用root根记录器
        """
        self.save_path = save_path
        self.log_level = log_level
        self.log_name = log_name
        self.StreamHandler_log_level = StreamHandler_log_level
        self.FileHandler_log_level = FileHandler_log_level

        if log_name is None:
            # 动态获取调用者的模块名作为logger名称
            import inspect
            frame = inspect.currentframe().f_back  # 获取调用栈的上一帧（调用者）
            log_name = frame.f_globals.get('__name__', 'root')  # 从调用者的全局变量中获取__name__

        # 确保日志文件所在目录存在，不存在则创建（包括多级目录）
        # 将相对路径转换为基于可执行文件目录的绝对路径
        save_path_obj = Path(self.save_path)
        if save_path_obj.is_absolute():
            abs_save_path = str(save_path_obj)
        else:
            abs_save_path = str(Path(get_app_path()) / save_path_obj)

        Path(abs_save_path).parent.mkdir(parents=True, exist_ok=True)
        self.save_path = abs_save_path

        # 初始化日志
        self.configure_handlers()

    def check_directory(self, check_path):
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
        # handler_Stream = logging.StreamHandler(sys.stdout)  # 控制台
        # handler_Stream.setFormatter(color_formatter)
        # handler_Stream.setLevel(self.StreamHandler_log_level)
        # self.logger.addHandler(handler_Stream)

        # 输出到文件按照时间分割
        handler_TimedRotatingFile = handlers.TimedRotatingFileHandler(self.save_path,  # 实际可使用self.save_path
                                                                      when='midnight',  # 每天午夜轮转
                                                                      interval=1,  # 每天轮转一次
                                                                      backupCount=7,  # 保留 7 个备份文件
                                                                      encoding='utf-8',
                                                                      delay=True)  # 延迟直到需要才单开
        handler_TimedRotatingFile.setFormatter(text_formatter)
        handler_TimedRotatingFile.setLevel(self.FileHandler_log_level)
        self.logger.addHandler(handler_TimedRotatingFile)
