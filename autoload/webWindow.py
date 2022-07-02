#!/usr/bin/env python3

from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6 import QtCore
from PyQt6.QtCore import QUrl, Qt, QEventLoop
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtNetwork import QNetworkProxy, QNetworkProxyFactory

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher

import platform
import sys
import signal
import os
import functools
import importlib
import threading


class PostGui(QtCore.QObject):
    through_thread = QtCore.pyqtSignal(object, object)

    def __init__(self, inclass=True):
        super(PostGui, self).__init__()
        self.through_thread.connect(self.on_signal_received)
        self.inclass = inclass

    def __call__(self, func):
        self._func = func

        @functools.wraps(func)
        def obj_call(*args, **kwargs):
            self.emit_signal(args, kwargs)
        return obj_call

    def emit_signal(self, args, kwargs):
        self.through_thread.emit(args, kwargs)

    def on_signal_received(self, args, kwargs):
        if self.inclass:
            obj, args = args[0], args[1:]
            self._func(obj, *args, **kwargs)
        else:
            self._func(*args, **kwargs)


class BrowserPage(QWebEnginePage):
    def __init__(self):
        QWebEnginePage.__init__(self)

    def execute_javascript(self, script_src):
        ''' Execute JavaScript.'''
        # Build event loop.
        self.loop = QEventLoop()

        # Run JavaScript code.
        self.runJavaScript(script_src, self.callback_js)

        # Execute event loop, and wait event loop quit.
        self.loop.exec()

        # Return JavaScript function result.
        return self.result

    def callback_js(self, result):
        ''' Callback of JavaScript, call loop.quit to jump code after loop.exec.'''
        self.result = result
        self.loop.quit()


class WebWindow(QWidget):
    def __init__(self):
        super().__init__()
        global screen_size

        if platform.system() == "Windows":
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint |
                                Qt.WindowType.Tool | Qt.WindowType.WindowDoesNotAcceptFocus)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                                Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip)
        self.setContentsMargins(0, 0, 0, 0)

        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.zoom_factor = 1
        if screen_size.width() > 3000:
            self.zoom_factor = 2

        self.loading_js_code = ""
        self.load_finish_callback = None

        self.dark_mode_js = open(os.path.join(
            os.path.dirname(__file__), "darkreader.js")).read()

        self.theme_mode = "dark"
        #  self.update_theme_mode()

        self.webview = QWebEngineView()
        self.web_page = BrowserPage()
        self.webview.setPage(self.web_page)

        #  self.web_page.setBackgroundColor(QColor(get_emacs_func_result("popweb-get-theme-background", [])))

        self.webview.loadStarted.connect(lambda: self.reset_zoom())
        self.webview.loadProgress.connect(
            lambda: self.execute_loading_js_code())
        self.webview.loadFinished.connect(self.execute_load_finish_js_code)
        self.reset_zoom()

        self.vbox.addWidget(self.webview)
        self.setLayout(self.vbox)

        self.webview.installEventFilter(self)

        self.settings = self.webview.settings()
        try:
            self.settings.setAttribute(
                QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
            self.settings.setAttribute(
                QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
            self.settings.setAttribute(
                QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
            self.settings.setAttribute(
                QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
            self.settings.setAttribute(
                QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            self.settings.setAttribute(
                QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            self.settings.setAttribute(
                QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        except Exception:
            import traceback
            traceback.print_exc()

    def reset_zoom(self):
        self.webview.setZoomFactor(self.zoom_factor)

    #  def update_theme_mode(self):
    #      self.theme_mode = get_emacs_func_result("popweb-get-theme-mode", [])

    def execute_loading_js_code(self):
        if self.loading_js_code != "":
            self.webview.page().runJavaScript(self.loading_js_code)

        if self.theme_mode == "dark":
            self.load_dark_mode_js()
            self.enable_dark_mode()

    def execute_load_finish_js_code(self):
        if self.load_finish_callback != None:
            self.load_finish_callback()

    def load_dark_mode_js(self):
        self.webview.page().runJavaScript(
            '''if (typeof DarkReader === 'undefined') {{ {} }} '''.format(self.dark_mode_js))

    def enable_dark_mode(self):
        ''' Dark mode support.'''
        self.webview.page().runJavaScript(
            """DarkReader.setFetchMethod(window.fetch); DarkReader.enable({brightness: 100, contrast: 90, sepia: 10});""")

    def disable_dark_mode(self):
        ''' Remove dark mode support.'''
        self.webview.page().runJavaScript("""DarkReader.disable();""")


class POPWEB(object):
    def __init__(self):
        global proxy_string

        self.web_window_dict = {}
        self.module_dict = {}

        # Disable use system proxy, avoid page slow when no network connected.
        QNetworkProxyFactory.setUseSystemConfiguration(False)

        #  self.proxy = (proxy_type, proxy_host, proxy_port)
        self.is_proxy = False

        dispatcher["call_module_method"] = self.call_module_method
        dispatcher["hide_web_window"] = self.hide_web_window

        self.server_thread = threading.Thread(target=lambda:
                                              run_simple(
                                                  'localhost', 4000, application)
                                              )
        self.server_thread.start()

    def get_web_window(self, module_name):
        if module_name not in self.web_window_dict:
            self.web_window_dict[module_name] = WebWindow()

        return self.web_window_dict[module_name]

    def get_module(self, module_path):
        if module_path not in self.module_dict:
            spec = importlib.util.spec_from_file_location(
                module_path, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.module_dict[module_path] = module

        return self.module_dict[module_path]

    @PostGui()
    def call_module_method(self, module_path, method_name, method_args):
        module = self.get_module(module_path)
        method_args.insert(0, self)
        return getattr(module, method_name)(*method_args)

    @PostGui()
    def hide_web_window(self, module_name):
        if module_name in self.web_window_dict:
            web_window = self.web_window_dict[module_name]
            web_window.hide()
            web_window.webview.load(QUrl(""))


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["add"] = lambda a, b: a + b
    dispatcher["exit"] = lambda : sys.exit(0)
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == "__main__":
    hardware_acceleration_args = []
    if platform.system() != "Windows":
        hardware_acceleration_args += [
            "--ignore-gpu-blocklist",
            "--enable-gpu-rasterization",
            "--enable-native-gpu-memory-buffers"]
    if platform.system() == "Darwin":
        import AppKit
        info = AppKit.NSBundle.mainBundle().infoDictionary()
        info["LSBackgroundOnly"] ="1"

    app = QApplication(["--disable-web-security"] + hardware_acceleration_args)
    screen = app.primaryScreen()
    screen_size = screen.size()

    popweb = POPWEB()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())
