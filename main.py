"""翻译工具 - 基于 NiceGUI 原生模式的桌面翻译应用

使用 NiceGUI native 模式（pywebview + WebView2）创建桌面窗口，
通过 iframe 嵌入翻译网页，支持窗口置顶、悬浮按钮拖动、配置持久化。
"""
import os

from nicegui import app, ui

from app.config import USER_DATA_DIR, load
from app.patch import patch_webview_args


def _set_initial_on_top():
    """窗口显示后设置初始置顶状态

    pywebview 的 create_window(on_top=True) 在 webview.start() 前不一定生效，
    因此在 'shown' 事件回调中通过 WindowProxy 再次确保置顶。
    """
    window = app.native.main_window
    if window is not None:
        window.set_always_on_top(True)


def main():
    """应用主入口：加载配置 → 补丁 WebView2 → 配置窗口 → 注册页面 → 启动"""
    settings = load()

    # 确保独立用户数据目录存在（pywebview 浏览器数据隔离存放）
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 补丁 WebView2：追加跨域参数、代理设置等
    patch_webview_args(
        proxy=settings['proxy'],
        proxy_username=settings['proxy_username'],
        proxy_password=settings['proxy_password'],
    )

    # 原生窗口参数（从配置读取尺寸和置顶状态）
    app.native.window_args.update({
        'title': '翻译工具 - Translate',
        'width': settings['window_width'],
        'height': settings['window_height'],
        'min_size': (300, 300),  # 最小窗口尺寸，防止过小导致布局异常
        'on_top': settings['window_on_top'],
    })

    # pywebview 启动参数：使用独立 storage_path 存储浏览器数据，与系统浏览器完全隔离
    app.native.start_args = {
        'storage_path': str(USER_DATA_DIR),
        'private_mode': False,
    }

    # 关闭窗口时强制退出程序（os._exit 避免 NiceGUI 后台线程阻止退出）
    app.native.on('closed', lambda: os._exit(0))

    # 窗口显示后设置初始置顶状态（pywebview 的 on_top 参数在 start 前不一定生效）
    if settings['window_on_top']:
        app.native.on('shown', lambda: _set_initial_on_top())

    # 注册翻译页面路由和 API 端点
    from app.pages.translate import create_page
    create_page(settings)

    # 启动 NiceGUI 原生窗口
    # native=True: 使用 pywebview 而非浏览器打开
    # reload=False: 关闭热重载（打包时必须）
    # storage_secret: NiceGUI 内部存储加密密钥
    ui.run(native=True, reload=False, storage_secret='translate-tool')


if __name__ == '__main__':
    main()
