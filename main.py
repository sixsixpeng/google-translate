"""翻译工具 - 基于 NiceGUI 原生模式"""
import os

from nicegui import app, ui

from app.config import USER_DATA_DIR, load
from app.patch import patch_disable_web_security


def _set_initial_on_top():
    """窗口显示后设置初始置顶状态"""
    window = app.native.main_window
    if window is not None:
        window.set_always_on_top(True)


def main():
    settings = load()

    # 确保独立用户数据目录存在
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 在 NiceGUI 启动前补丁 WebView2，追加 --disable-web-security 以允许 iframe 跨域
    patch_disable_web_security()

    # 原生窗口参数（从配置读取尺寸）
    app.native.window_args.update({
        'title': '翻译工具',
        'width': settings['window_width'],
        'height': settings['window_height'],
        'min_size': (300, 300),
        'on_top': settings['window_on_top'],
    })

    # pywebview 启动参数（隔离浏览器数据）
    app.native.start_args = {
        'storage_path': str(USER_DATA_DIR),
        'private_mode': False,
    }

    # 关闭窗口时退出程序
    app.native.on('closed', lambda: os._exit(0))

    # 窗口显示后设置初始置顶状态（pywebview 的 on_top 参数在 start 前不一定生效）
    if settings['window_on_top']:
        app.native.on('shown', lambda: _set_initial_on_top())

    # 注册翻译页面
    from app.pages.translate import create_page
    create_page(settings)

    ui.run(native=True, reload=False, storage_secret='translate-tool')


if __name__ == '__main__':
    main()
