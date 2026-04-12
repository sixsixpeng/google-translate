import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PySide6.QtNetwork import QNetworkProxy


class CustomWebEnginePage(QWebEnginePage):
    """自定义页面，处理剪贴板权限请求"""

    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        # 监听权限请求
        self.featurePermissionRequested.connect(self.on_feature_permission_requested)

    def on_feature_permission_requested(self, security_origin, feature):
        """当网页请求特定权限时调用"""
        # 允许剪贴板读取权限（仅对翻译域名）
        if feature == QWebEnginePage.Feature.ClipboardRead:
            origin_url = security_origin.toString()
            if "translate" in origin_url or "tantu.com" in origin_url:
                print(f"✅ 已授权剪贴板访问: {origin_url}")
                self.setFeaturePermission(
                    security_origin,
                    feature,
                    QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
                )
            else:
                print(f"❌ 拒绝剪贴板访问: {origin_url}")
                self.setFeaturePermission(
                    security_origin,
                    feature,
                    QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
                )

    def triggerAction(self, action, checked=False):
        """处理粘贴动作"""
        paste_actions = [
            QWebEnginePage.WebAction.Paste,
            QWebEnginePage.WebAction.PasteAndMatchStyle,
        ]
        if action in paste_actions:
            print(f"📋 触发粘贴动作")
        super().triggerAction(action, checked)


class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Translate")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # 居中
        self.setGeometry((QApplication.primaryScreen().geometry().width() - 800) // 2,
                         (QApplication.primaryScreen().geometry().height() - 400) // 2
                         , 800, 500)

        # 1. 配置 WebEngine 设置（必须在创建 WebEngineView 之前）
        self.setup_webengine_settings()

        # 2. 设置代理（根据需要修改）
        # self.setup_proxy(
        #     proxy_url="127.0.0.1",  # 代理服务器地址
        #     proxy_port=7890,  # 代理端口
        #     username=None,  # 用户名（没有则设为 None）
        #     password=None  # 密码（没有则设为 None）
        # )

        # 3. 创建界面
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 4. 创建 WebEngineView 并配置
        self.browser = QWebEngineView()

        # 配置 Profile
        profile = QWebEngineProfile.defaultProfile()
        # 设置自定义 User-Agent，让请求更真实
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        # 使用自定义页面（处理剪贴板权限）
        custom_page = CustomWebEnginePage(profile, self.browser)
        self.browser.setPage(custom_page)

        # 使用代理地址（注释掉官方地址）
        # self.browser.setUrl(QUrl("https://translate.google.com"))
        self.browser.setUrl(QUrl("https://google-translate-proxy.tantu.com/"))

        layout.addWidget(self.browser)

        # 监听页面加载完成
        self.browser.loadFinished.connect(self.on_load_finished)

    def setup_webengine_settings(self):
        """配置 WebEngine 全局设置，启用剪贴板访问"""
        # 修复：使用 defaultProfile() 获取设置，而不是直接调用 defaultSettings()
        profile = QWebEngineProfile.defaultProfile()
        settings = profile.settings()

        # 关键：启用剪贴板访问（必须设置）
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)

        # 可选：其他有用设置
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)  # 启用本地存储
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)  # 启用插件
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)  # 启用 WebGL

        print("✅ WebEngine 设置已配置（剪贴板访问已启用）")

    def setup_proxy(self, proxy_url, proxy_port, username=None, password=None):
        """配置代理（支持用户名密码认证）"""
        if not proxy_url or not proxy_port:
            print("ℹ️ 未配置代理，将直接连接")
            return

        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.ProxyType.HttpProxy)
        proxy.setHostName(proxy_url)
        proxy.setPort(proxy_port)

        if username and password:
            proxy.setUser(username)
            proxy.setPassword(password)
            print(f"🔐 代理已设置: {proxy_url}:{proxy_port} (使用认证用户: {username})")
        else:
            print(f"🌐 代理已设置: {proxy_url}:{proxy_port} (无认证)")

        QNetworkProxy.setApplicationProxy(proxy)

    def on_load_finished(self, ok):
        """页面加载完成后的回调"""
        if ok:
            print("✅ 翻译页面已加载完成")
            print("📌 使用说明:")
            print("   1. 文字翻译: 直接输入文字")
            print("   2. 图片翻译: 截图后，在网页中按 Ctrl+V 粘贴")
            print("   3. 文档翻译: 点击'文档'图标上传文件")

            # 注入提示信息到网页控制台
            self.browser.page().runJavaScript("""
                console.log('=== PySide6 翻译工具已就绪 ===');
                console.log('支持功能:');
                console.log('- 文字翻译');
                console.log('- 图片翻译（直接 Ctrl+V 粘贴）');
                console.log('- 文档翻译');
            """)
        else:
            print("❌ 页面加载失败，请检查网络连接或代理设置")

    def closeEvent(self, event):
        """关闭窗口时的清理工作"""
        print("👋 翻译工具已关闭")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())
