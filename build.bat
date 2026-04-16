选项1 - 文件夹模式 + 有控制台（调试用，可看到日志）
pyinstaller -D --name="google-translate" --icon="icon.ico"  main.py

选项2 - 文件夹模式 + 无控制台（生产推荐，启动快，界面简洁）
pyinstaller -D --noconsole --name="google-translate" --icon="icon.ico"  main.py

选项3 - 单文件模式 + 有控制台（调试用，可看到日志，但启动慢）
pyinstaller -F --name="google-translate" --icon="icon.ico"  main.py


选项4 - 单文件模式 + 无控制台（便携分发，启动慢，只有一个文件）
pyinstaller -F --noconsole --name="google-translate" --icon="icon.ico"  main.py
