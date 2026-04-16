# -*- coding: UTF-8 -*-
# 2026/4/16 00:49

from pynput import keyboard

from enmu_data import p_task
from logger import Logger

logger = Logger(f"./logs/{__name__}.log", log_name=__name__).logger


class HotkeyListener:
    """
    键盘热键监听
    """

    def __init__(self, PROCESS_TASK_LIST):
        self.THREAD_TASK_LIST = PROCESS_TASK_LIST

        self.listening_method()

    def text_translation(self):
        logger.debug('<alt>+v pressed,触发文字翻译')
        self.THREAD_TASK_LIST.put(p_task("text_translation"))

    def img_translation(self):
        logger.debug('<alt>+x pressed,触发图片翻译')
        self.THREAD_TASK_LIST.put(p_task("img_translation"))

    def listening_method(self):
        self.listen = keyboard.GlobalHotKeys({'<alt>+v': self.text_translation,
                                              '<alt>+x': self.img_translation,
                                              })

        self.listen.start()
        self.listen.join()
