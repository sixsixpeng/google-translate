# -*- coding: UTF-8 -*-
# 2026/4/16 00:52

from multiprocessing import Process
from threading import Thread
from logger import Loger

logger = Loger().logger


def process_run(func, *args, **kwargs):
    """
    独立进程去执行任务
    """
    TASK = Process(target=func, args=args, kwargs=kwargs)
    logger.debug(f"启动独立进程,执行任务：{func.__name__},进程ID：{TASK.pid}")
    TASK.start()
    return TASK


def Thread_run(func, *args, **kwargs):
    """
    独立线程去执行任务
    """
    TASK = Thread(target=func, args=args, kwargs=kwargs)
    TASK.daemon = True  # 设置为守护线程，主线程结束时自动终止
    logger.debug(f"启动独立线程,执行任务：{func.__name__},线程ID：{TASK.ident}")
    TASK.start()
    return TASK


def kill_all_process(PROCESS_TASK_LIST, THREAD_TASK_LIST):
    """
    安全结束所有进程和线程
    """
    logger.debug("结束所有进程")

    # 终止所有子进程
    for task in PROCESS_TASK_LIST:
        if task.is_alive():
            logger.debug(f"终止进程：{task.pid}")
            task.terminate()
            task.join(timeout=5)  # 等待最多5秒
            if task.is_alive():
                logger.warning(f"强制杀死进程：{task.pid}")
                task.kill()

    # 线程无法强制终止，只能等待其自然结束
    # 如果需要停止线程，应该在任务中设置停止标志
    active_threads = [t for t in THREAD_TASK_LIST if t.is_alive()]
    logger.debug(f"活跃线程数：{len(active_threads)}")

    logger.debug("关闭窗口")