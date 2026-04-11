# Google 翻译工具

基于 Python + NiceGUI 原生模式构建的桌面翻译小工具，iframe 嵌入翻译页面，支持窗口置顶、回到首页、浏览器数据隔离。

## 功能特性

- NiceGUI 原生窗口，iframe 直接加载翻译网页
- 「回到翻译首页」按钮，防止跳转后无法返回
- 窗口置顶开关，状态持久化保存
- 悬浮按钮可拖动，位置自动记忆
- 独立隔离浏览器环境，不影响本地 Edge/Chrome 数据
- INI 格式配置文件，可自定义翻译地址
- 关闭窗口即退出程序

## 项目结构

```
google-translate/
├── main.py                  # 程序入口
├── build.bat                # 一键构建打包
├── requirements.txt         # Python 依赖
├── config.ini               # 配置文件（首次运行自动生成）
├── browser_data/            # 浏览器隔离数据（自动生成）
└── app/
    ├── __init__.py
    ├── config.py            # 配置管理
    ├── patch.py             # WebView2 跨域补丁
    └── pages/
        ├── __init__.py
        └── translate.py     # 翻译页面
```

## 快速开始

### 环境要求

- Python 3.10+
- Windows：需已安装 WebView2 运行时（Windows 10/11 通常自带）

### 安装依赖

```bash
pip install -r requirements.txt
```

> `nicegui[native]>=2.0` 会自动安装 pywebview 等原生窗口依赖。

### 启动程序

```bash
python main.py
```

## 配置说明

首次启动会在项目根目录自动生成 `config.ini`：

```ini
[general]
translate_url = https://google-translate-proxy.tantu.com/
window_on_top = true
window_width = 1100
window_height = 750
btn_home_x = 10
btn_home_y = 10
btn_top_x = 10
btn_top_y = 50
```

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `translate_url` | 翻译页面地址 | `https://google-translate-proxy.tantu.com/` |
| `window_on_top` | 窗口是否置顶 | `true` |
| `window_width` | 窗口宽度 | `1100` |
| `window_height` | 窗口高度 | `750` |
| `btn_home_x/y` | 首页按钮位置 | `10/10` |
| `btn_top_x/y` | 置顶按钮位置 | `10/50` |

### 切换为百度翻译

修改 `config.ini` 中的 `translate_url`：

```ini
translate_url = https://fanyi.baidu.com/mtpe-individual/transText#/
```

## 行为说明

- 关闭窗口 → 退出整个程序
- 悬浮「🏠 首页」按钮可将 iframe 重置为翻译主页，可拖动
- 悬浮「📌 置顶」按钮可切换窗口置顶状态，可拖动，位置自动保存
- 浏览器数据存储在项目目录 `browser_data/` 下，与本地浏览器完全隔离
