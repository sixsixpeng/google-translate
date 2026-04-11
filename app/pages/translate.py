"""翻译页面模块

注册 NiceGUI 页面路由和 HTTP API 端点，实现：
- 全屏 iframe 嵌入翻译网页
- 两个可拖动悬浮按钮（首页、置顶）
- 按钮位置持久化保存
- 窗口置顶状态切换
- iframe 内容随窗口缩放自适应
"""

from nicegui import app, ui
from pydantic import BaseModel

from app.config import save

# iframe 缩放基准宽度：当窗口宽度小于此值时，iframe 内容按比例缩小
BASE_WIDTH = 1100


class BtnPosData(BaseModel):
    """按钮位置数据模型，用于接收前端拖拽结束后的位置保存请求"""
    key: str  # 按钮标识：'home' 或 'top'
    x: int  # 按钮左偏移量（px）
    y: int  # 按钮上偏移量（px）


def create_page(settings: dict):
    """注册翻译页面路由和 API 端点

    Args:
        settings: 配置字典，包含 translate_url、window_on_top、按钮位置等
    """
    translate_url = settings['translate_url']

    @app.post('/save_btn_pos')
    def save_btn_pos(data: BtnPosData):
        """保存悬浮按钮拖拽后的位置到配置文件"""
        if data.key == 'home':
            save('btn_home_x', str(data.x))
            save('btn_home_y', str(data.y))
        elif data.key == 'top':
            save('btn_top_x', str(data.x))
            save('btn_top_y', str(data.y))

    @app.post('/toggle_top')
    async def toggle_top():
        """切换窗口置顶状态

        通过 NiceGUI 的 WindowProxy.set_always_on_top() 在主线程执行，
        避免 pywebview 跨线程操作导致失败。
        同时更新内存中的 settings 和配置文件。
        """
        new_top = not settings['window_on_top']

        # 通过 NiceGUI 的 WindowProxy 在主线程设置置顶
        window = app.native.main_window
        if window is not None:
            window.set_always_on_top(new_top)

        # 同步更新内存中的窗口参数和配置文件
        app.native.window_args['on_top'] = new_top
        save('window_on_top', str(new_top).lower())
        settings['window_on_top'] = new_top

        return {'on_top': new_top}

    @ui.page('/')
    def index():
        """翻译主页面

        页面结构：
        1. 全屏 iframe 嵌入翻译网页
        2. 两个悬浮可拖动按钮（首页、置顶）
        3. JavaScript 处理拖拽、点击、iframe 缩放逻辑
        """
        # 隐藏页面滚动条，让 iframe 完全占满
        ui.query('html, body').style(
            'overflow: hidden; margin: 0; padding: 0; width: 100%; height: 100%'
        )

        # 全屏 iframe：加载翻译网页，允许剪贴板读写
        # transform-origin: top left 确保缩放时以左上角为锚点
        ui.element('iframe').props(
            f'src={translate_url} allow="clipboard-read; clipboard-write"'
        ).style(
            'position: fixed; top: 0; left: 0; right: 0; bottom: 0; '
            'width: 100%; height: 100%; border: none; transform-origin: top left;'
        )

        # 悬浮按钮 HTML（位置从配置读取，支持拖动）
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

        # 前端交互逻辑：拖拽、点击、iframe 缩放
        # 使用 ui.run_javascript() 而非 ui.html() 中的 <script>，
        # 因为 NiceGUI 禁止 ui.html() 包含 <script> 标签，
        # 且 run_javascript 保证在 DOM 就绪后执行
        ui.run_javascript(f'''
            // === 拖拽逻辑 ===
            // makeDraggable: 为按钮绑定 mousedown/mousemove/mouseup 事件
            // 通过 2px 阈值区分「点击」和「拖拽」操作
            function makeDraggable(el, configKey) {{
                var dragging = false, wasDragged = false, startX, startY, startLeft, startTop;

                // 按下鼠标：记录起始位置
                el.addEventListener('mousedown', function(e) {{
                    if (e.button !== 0) return;  // 仅响应左键
                    dragging = true;
                    wasDragged = false;
                    startX = e.clientX;
                    startY = e.clientY;
                    startLeft = el.offsetLeft;
                    startTop = el.offsetTop;
                    e.preventDefault();  // 防止选中文本
                }});

                // 移动鼠标：超过 2px 阈值视为拖拽，更新按钮位置
                document.addEventListener('mousemove', function(e) {{
                    if (!dragging) return;
                    var dx = e.clientX - startX;
                    var dy = e.clientY - startY;
                    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) wasDragged = true;
                    if (!wasDragged) return;
                    // 限制按钮不超出视口边界
                    var newLeft = Math.max(0, Math.min(startLeft + dx, window.innerWidth - el.offsetWidth));
                    var newTop = Math.max(0, Math.min(startTop + dy, window.innerHeight - el.offsetHeight));
                    el.style.left = newLeft + 'px';
                    el.style.top = newTop + 'px';
                }});

                // 松开鼠标：若为拖拽则保存位置到配置
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

                // 点击按钮：区分点击和拖拽，执行对应操作
                el.addEventListener('click', function(e) {{
                    if (wasDragged) {{
                        e.preventDefault();
                        e.stopPropagation();
                        wasDragged = false;
                        return;
                    }}
                    if (configKey === 'home') {{
                        // 首页按钮：重置 iframe 地址回到翻译首页
                        document.querySelector('iframe').src = '{translate_url}';
                    }} else if (configKey === 'top') {{
                        // 置顶按钮：切换置顶状态并更新按钮文字
                        fetch('/toggle_top', {{method: 'POST'}})
                            .then(function(r) {{ return r.json(); }})
                            .then(function(d) {{
                                el.textContent = d.on_top ? '📌 置顶中' : '📌 置顶';
                            }});
                    }}
                }});
            }}

            // 初始化两个悬浮按钮的拖拽功能
            var homeBtn = document.getElementById('__home_btn');
            var topBtn = document.getElementById('__top_btn');
            if (homeBtn) makeDraggable(homeBtn, 'home');
            if (topBtn) makeDraggable(topBtn, 'top');

            // === iframe 缩放逻辑 ===
            // 当窗口宽度小于 BASE_WIDTH 时，按比例缩小 iframe 内容，
            // 避免出现水平滚动条；窗口足够宽时不缩放
            function scaleIframe() {{
                var frame = document.querySelector('iframe');
                if (!frame) return;
                var currentWidth = document.documentElement.clientWidth;
                if (currentWidth < {BASE_WIDTH}) {{
                    var scale = currentWidth / {BASE_WIDTH};
                    frame.style.transform = 'scale(' + scale + ')';
                    frame.style.width = '{BASE_WIDTH}px';
                    // 高度需要除以缩放比，确保可视区域填满窗口
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
