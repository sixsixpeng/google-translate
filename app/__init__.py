"""app 包

注意：此文件保持为空，不在包级别导入任何模块。
原因：pywebview / pythonnet 的导入会触发 CLR 初始化，
在 __init__.py 中导入会导致 import app 时阻塞卡死。
所有需要的模块在 main.py 中按需导入。
"""
