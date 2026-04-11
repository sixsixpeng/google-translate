from nicegui import app, ui
import os
import platform
import ctypes
import time

# ===================== 【填写你的公司代理】 =====================
PROXY_HOST = "proxy.公司.com"
PROXY_PORT = "8080"
PROXY_USER = "你的账号"
PROXY_PASS = "你的密码"


# =================================================================

# ===================== 设置全局代理（带账号密码，唯一有效方式） =====================
def configure_proxy():
    proxy_full = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    os.environ["HTTP_PROXY"] = proxy_full
    os.environ["HTTPS_PROXY"] = proxy_full
    os.environ["ALL_PROXY"] = proxy_full


# ===================== 窗口置顶（Windows） =====================
def set_always_on_top():
    if platform.system() != "Windows":
        return
    try:
        time.sleep(1)
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        hwnd = user32.GetForegroundWindow()
        user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
    except Exception:
        pass


# ===================== 页面 =====================
@ui.page("/")
def index():
    ui.query("body").style("margin:0; padding:0; overflow:hidden;")
    # 内嵌谷歌翻译
    ui.html('''
    <iframe 
        src="https://translate.google.com" 
        width="100%" 
        height="100%" 
        frameborder="0">
    </iframe>
    ''').classes("w-full h-screen")


# ===================== 启动（无任何错误参数） =====================
configure_proxy()
app.on_startup(set_always_on_top)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="置顶翻译器（公司内网版）",
        native=True,
        window_size=(450, 700),
        reload=False,
    )
