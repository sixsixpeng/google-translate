"""WebView2 补丁模块

通过猴子补丁（monkey-patch）修改 pywebview 的 EdgeChrome.__init__，
在 AdditionalBrowserArguments 中追加额外参数，并在 on_webview_ready 中
注册代理认证事件处理。

追加的参数：
  - --disable-web-security: 禁用同源策略，允许 iframe 跨域
  - --allow-file-access-from-files: 允许本地文件互相访问
  - --proxy-server: HTTP 代理地址（配置非空时生效）

注意：此补丁必须在 NiceGUI/pywebview 启动前调用，且不能在 app/__init__.py
中导入执行，否则会触发 pythonnet/CLR 初始化导致应用卡死。
"""
import inspect
import textwrap

# 模块级变量，供 patch_webview_args() 写入后由 _patched_on_webview_ready 读取
_proxy_username = ''
_proxy_password = ''


def patch_webview_args(proxy: str = '', proxy_username: str = '', proxy_password: str = ''):
    """补丁 WebView2，追加跨域、代理等浏览器参数

    Args:
        proxy: 代理地址，格式如 http://127.0.0.1:7890，为空则不设置代理
        proxy_username: 代理认证用户名，为空则不设置认证
        proxy_password: 代理认证密码
    """
    global _proxy_username, _proxy_password
    _proxy_username = proxy_username
    _proxy_password = proxy_password

    try:
        from webview.platforms import edgechromium

        # 获取 __init__ 源码并去除缩进
        source = inspect.getsource(edgechromium.EdgeChrome.__init__)
        source = textwrap.dedent(source)

        # 在 AdditionalBrowserArguments 字符串末尾追加跨域参数
        # WebView2 的 AdditionalBrowserArguments 接受空格分隔的多参数格式
        extra_args = '--disable-web-security --allow-file-access-from-files'
        if proxy:
            extra_args += f' --proxy-server={proxy}'
        source = source.replace(
            "'--disable-features=ElasticOverscroll'",
            f"'--disable-features=ElasticOverscroll {extra_args}'",
            1,
        )

        # 重新编译并替换原方法
        module_globals = dict(vars(edgechromium))
        code = compile(source, '<patched_init>', 'exec')
        exec(code, module_globals)
        edgechromium.EdgeChrome.__init__ = module_globals['EdgeChrome'].__init__

        # 补丁 on_webview_ready，注入代理认证事件
        if proxy_username:
            _patch_auth_handler(edgechromium)

    except Exception as e:
        print(f'[WARN] WebView2 patch failed: {e}, iframe may not load cross-origin pages')


def _patch_auth_handler(edgechromium_module):
    """补丁 on_webview_ready，注册 BasicAuthenticationRequested 事件处理代理认证

    WebView2 在遇到代理要求身份验证时会触发 BasicAuthenticationRequested 事件，
    通过该事件自动填入用户名和密码，避免弹出认证对话框。
    """
    ready_src = inspect.getsource(edgechromium_module.EdgeChrome.on_webview_ready)
    ready_src = textwrap.dedent(ready_src)

    # 在 on_webview_ready 方法末尾（最后一行前）插入代理认证事件注册
    auth_handler_code = (
        "        # === 代理认证补丁 ===\n"
        "        sender.CoreWebView2.BasicAuthenticationRequested += self._on_proxy_auth\n"
    )

    # 在方法末尾插入（在最后一个 return 或方法结尾之前）
    # 找到方法最后一行非空内容的位置，在其前插入
    lines = ready_src.rstrip().split('\n')
    # 在最后一行后追加
    ready_src = ready_src.rstrip() + '\n' + auth_handler_code

    module_globals = dict(vars(edgechromium_module))
    code = compile(ready_src, '<patched_on_webview_ready>', 'exec')
    exec(code, module_globals)
    edgechromium_module.EdgeChrome.on_webview_ready = module_globals['EdgeChrome'].on_webview_ready

    # 添加代理认证处理方法到类上
    def _on_proxy_auth(self, sender, args):
        """WebView2 代理认证回调，自动填入用户名和密码"""
        try:
            from Microsoft.Web.WebView2.Core import CoreWebView2BasicAuthenticationResponse
            args.Response.UserName = _proxy_username
            args.Response.Password = _proxy_password
        except Exception:
            pass

    edgechromium_module.EdgeChrome._on_proxy_auth = _on_proxy_auth
