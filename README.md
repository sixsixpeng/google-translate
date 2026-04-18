# Google Translate Tool

一款基于 Playwright + pywebview 的桌面翻译工具，支持全局热键快速翻译。

---

## 功能特性

- **全局热键翻译**：无需切换窗口，通过快捷键即可触发翻译
  - `Alt + V` 文字翻译
  - `Alt + X` 图片翻译
- **无界面浏览器**：基于 Playwright 驱动的 Google 翻译服务
- **轻量级**：使用 pywebview 构建简洁界面
- **跨平台**：支持 Windows 系统

---

## 环境要求

- **Python**: 3.10+
- **操作系统**: Windows 10/11

---

## 安装依赖

```bash
# 1. 克隆项目
git clone <repository-url>
cd google-translate

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 独立环境打包项目
pyinstaller --onefile --windowed --icon=icon.ico main.py
```
```bash
# 选项1 - 文件夹模式 + 有控制台（调试用，可看到日志）
pyinstaller -D --name="Translate" --icon="icon.ico"  main.py

# 选项2 - 文件夹模式 + 无控制台（生产推荐，启动快，界面简洁）
pyinstaller -D --noconsole --name="Translate" --icon="icon.ico"  main.py

# 选项3 - 单文件模式 + 有控制台（调试用，可看到日志，但启动慢）
pyinstaller -F --name="Translate" --icon="icon.ico"  main.py


# 选项4 - 单文件模式 + 无控制台（便携分发，启动慢，只有一个文件）
pyinstaller -F --noconsole --name="Translate" --icon="icon.ico"  main.py
```


### requirements.txt

```
pywebview
playwright
pynput
```

---

## 使用方法

### 开发模式运行

```bash
python main.py
```

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Alt + V` | 触发文字翻译 |
| `Alt + X` | 触发图片翻译 |

### 日志查看

运行后会自动生成以下目录：
- `logs/` - 日志文件目录
- `cache/` - 缓存目录



### 打包后目录结构

```
dist/google-translate/
├── google-translate.exe      # 主程序
├── icon.ico                  # 图标文件
├── icon.png                  # PNG 图标
├── ms-playwright/            # Playwright 浏览器驱动
├── logs/                     # 日志目录（运行时创建）
└── cache/                    # 缓存目录（运行时创建）
```

### 分发说明

**文件夹模式**：将 `dist/google-translate/` 整个文件夹压缩发送，接收者解压后双击 `google-translate.exe` 即可运行。

**单文件模式**：直接将 `dist/google-translate.exe` 发送给用户，双击运行即可。

---

## 项目结构

```
google-translate/
├── main.py                   # 主程序入口
├── Hotkey.py                 # 全局热键监听
├── Playwright_translate.py   # Playwright 翻译模块
├── enmu_data.py              # 数据类和枚举定义
├── logger.py                 # 日志工具
├── build.bat                 # 打包脚本
├── icon.ico                  # 程序图标
├── icon.png                  # PNG 图标
└── requirements.txt          # Python 依赖
```

---

## 常见问题

### Q: 打包后运行窗口重复打开
A: 确保在 `main.py` 的 `if __name__ == '__main__':` 中添加了 `multiprocessing.freeze_support()`

### Q: 热键不生效
A: 确保程序正在前台运行，部分安全软件可能阻止全局热键。

### Q: 翻译功能无法使用
A: 检查网络连接，确保可以正常访问 Google 翻译服务。

---

## 开发说明

### 代码规范

- 使用 `pathlib` 处理路径
- 日志使用统一格式，便于排查问题
- 模块化设计，便于维护和扩展

### 添加新功能

1. 在对应模块中实现功能
2. 在 `enmu_data.py` 中定义任务类型
3. 在 `main.py` 中创建任务并加入队列

---

## 许可证

本项目仅供学习交流使用。

---

**最后更新**：2026-04-16
