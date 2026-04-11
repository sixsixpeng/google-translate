"""WebView2 补丁：追加 --disable-web-security 以允许 iframe 跨域加载"""

import inspect
import textwrap


def patch_disable_web_security():
    try:
        from webview.platforms import edgechromium

        source = inspect.getsource(edgechromium.EdgeChrome.__init__)
        source = textwrap.dedent(source)
        source = source.replace(
            "'--disable-features=ElasticOverscroll'",
            "'--disable-features=ElasticOverscroll --disable-web-security'",
            1,
        )

        module_globals = dict(vars(edgechromium))
        code = compile(source, '<patched_init>', 'exec')
        exec(code, module_globals)
        edgechromium.EdgeChrome.__init__ = module_globals['EdgeChrome'].__init__
    except Exception as e:
        print(f'[WARN] WebView2 patch failed: {e}, iframe may not load cross-origin pages')
