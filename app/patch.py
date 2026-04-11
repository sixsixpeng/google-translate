"""WebView2 补丁：追加 --disable-web-security 以允许 iframe 跨域加载

默认情况下 WebView2 遵循同源策略，禁止 iframe 加载跨域页面。
本模块通过猴子补丁（monkey-patch）修改 pywebview 的 EdgeChrome.__init__，
在 AdditionalBrowserArguments 中追加安全相关参数：
  - --disable-web-security: 禁用同源策略，允许 iframe 跨域
  - --allow-file-access-from-files: 允许本地文件互相访问

注意：此补丁必须在 NiceGUI/pywebview 启动前调用，且不能在 app/__init__.py
中导入执行，否则会触发 pythonnet/CLR 初始化导致应用卡死。
"""
import inspect
import textwrap


def patch_disable_web_security():
    """补丁 WebView2 的 EdgeChrome.__init__，追加跨域和安全参数

    通过 inspect 获取 EdgeChrome.__init__ 源码，将 AdditionalBrowserArguments
    中的 --disable-features=ElasticOverscroll 替换为包含额外安全参数的版本，
    然后重新编译并替换原方法。
    """
    try:
        from webview.platforms import edgechromium

        # 获取 __init__ 源码并去除缩进
        source = inspect.getsource(edgechromium.EdgeChrome.__init__)
        source = textwrap.dedent(source)

        # 在 AdditionalBrowserArguments 字符串末尾追加跨域参数
        # WebView2 的 AdditionalBrowserArguments 接受空格分隔的多参数格式
        source = source.replace(
            "'--disable-features=ElasticOverscroll'",
            "'--disable-features=ElasticOverscroll --disable-web-security --allow-file-access-from-files'",
            1,
        )

        # 重新编译并替换原方法
        module_globals = dict(vars(edgechromium))
        code = compile(source, '<patched_init>', 'exec')
        exec(code, module_globals)
        edgechromium.EdgeChrome.__init__ = module_globals['EdgeChrome'].__init__
    except Exception as e:
        # 补丁失败不影响启动，仅打印警告（iframe 跨域功能将不可用）
        print(f'[WARN] WebView2 patch failed: {e}, iframe may not load cross-origin pages')
