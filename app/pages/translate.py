"""翻译页面"""

from nicegui import app, ui
from pydantic import BaseModel

from app.config import save

BASE_WIDTH = 1100


class BtnPosData(BaseModel):
    key: str
    x: int
    y: int


def create_page(settings: dict):
    """注册翻译页面路由和内容"""
    translate_url = settings['translate_url']

    @app.post('/save_btn_pos')
    def save_btn_pos(data: BtnPosData):
        if data.key == 'home':
            save('btn_home_x', str(data.x))
            save('btn_home_y', str(data.y))
        elif data.key == 'top':
            save('btn_top_x', str(data.x))
            save('btn_top_y', str(data.y))

    @app.post('/toggle_top')
    async def toggle_top():
        new_top = not settings['window_on_top']

        # 通过 NiceGUI 的 WindowProxy 在主线程设置置顶
        window = app.native.main_window
        if window is not None:
            window.set_always_on_top(new_top)

        app.native.window_args['on_top'] = new_top
        save('window_on_top', str(new_top).lower())
        settings['window_on_top'] = new_top

        return {'on_top': new_top}

    @ui.page('/')
    def index():
        # 页面基础样式
        ui.query('html, body').style(
            'overflow: hidden; margin: 0; padding: 0; width: 100%; height: 100%'
        )

        # iframe：全屏
        ui.element('iframe').props(
            f'src={translate_url} allow="clipboard-read; clipboard-write"'
        ).style(
            'position: fixed; top: 0; left: 0; right: 0; bottom: 0; '
            'width: 100%; height: 100%; border: none; transform-origin: top left;'
        )

        # 悬浮按钮 HTML
        on_top = settings['window_on_top']
        top_label = '📌 置顶中' if on_top else '📌 置顶'

        ui.html(f'''
        <button id="__home_btn"
            style="position:fixed;left:{settings['btn_home_x']}px;top:{settings['btn_home_y']}px;
            z-index:99999;cursor:move;user-select:none;background:#fff;
            border:none;border-radius:20px;box-shadow:0 2px 8px rgba(0,0,0,0.25);
            padding:6px 14px;font-size:13px;color:#1d4ed8;
            font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;">
            🏠 首页
        </button>
        <button id="__top_btn"
            style="position:fixed;left:{settings['btn_top_x']}px;top:{settings['btn_top_y']}px;
            z-index:99999;cursor:move;user-select:none;background:#fff;
            border:none;border-radius:20px;box-shadow:0 2px 8px rgba(0,0,0,0.25);
            padding:6px 14px;font-size:13px;color:#1d4ed8;
            font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;">
            {top_label}
        </button>
        ''')

        # 拖拽 + 点击 + iframe 缩放，全部通过 run_javascript 在 DOM 就绪后执行
        ui.run_javascript(f'''
            // === 拖拽逻辑 ===
            function makeDraggable(el, configKey) {{
                var dragging = false, wasDragged = false, startX, startY, startLeft, startTop;

                el.addEventListener('mousedown', function(e) {{
                    if (e.button !== 0) return;
                    dragging = true;
                    wasDragged = false;
                    startX = e.clientX;
                    startY = e.clientY;
                    startLeft = el.offsetLeft;
                    startTop = el.offsetTop;
                    e.preventDefault();
                }});

                document.addEventListener('mousemove', function(e) {{
                    if (!dragging) return;
                    var dx = e.clientX - startX;
                    var dy = e.clientY - startY;
                    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) wasDragged = true;
                    if (!wasDragged) return;
                    var newLeft = Math.max(0, Math.min(startLeft + dx, window.innerWidth - el.offsetWidth));
                    var newTop = Math.max(0, Math.min(startTop + dy, window.innerHeight - el.offsetHeight));
                    el.style.left = newLeft + 'px';
                    el.style.top = newTop + 'px';
                }});

                document.addEventListener('mouseup', function() {{
                    if (!dragging) return;
                    dragging = false;
                    if (wasDragged) {{
                        fetch('/save_btn_pos', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{key: configKey, x: el.offsetLeft, y: el.offsetTop}})
                        }});
                    }}
                }});

                el.addEventListener('click', function(e) {{
                    if (wasDragged) {{
                        e.preventDefault();
                        e.stopPropagation();
                        wasDragged = false;
                        return;
                    }}
                    if (configKey === 'home') {{
                        document.querySelector('iframe').src = '{translate_url}';
                    }} else if (configKey === 'top') {{
                        fetch('/toggle_top', {{method: 'POST'}})
                            .then(function(r) {{ return r.json(); }})
                            .then(function(d) {{
                                el.textContent = d.on_top ? '📌 置顶中' : '📌 置顶';
                            }});
                    }}
                }});
            }}

            var homeBtn = document.getElementById('__home_btn');
            var topBtn = document.getElementById('__top_btn');
            if (homeBtn) makeDraggable(homeBtn, 'home');
            if (topBtn) makeDraggable(topBtn, 'top');

            // === iframe 缩放 ===
            function scaleIframe() {{
                var frame = document.querySelector('iframe');
                if (!frame) return;
                var currentWidth = document.documentElement.clientWidth;
                if (currentWidth < {BASE_WIDTH}) {{
                    var scale = currentWidth / {BASE_WIDTH};
                    frame.style.transform = 'scale(' + scale + ')';
                    frame.style.width = '{BASE_WIDTH}px';
                    frame.style.height = 'calc(100% / ' + scale + ')';
                }} else {{
                    frame.style.transform = 'none';
                    frame.style.width = '100%';
                    frame.style.height = '100%';
                }}
            }}
            scaleIframe();
            window.addEventListener('resize', scaleIframe);
        ''')
