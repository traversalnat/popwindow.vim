from PyQt6.QtCore import QUrl

def pop_url_window(popweb, module_name, x, y, frame_x, frame_y, frame_w, frame_h, width_scale, height_scale, url, js_code):
    print(x, y)
    web_window = popweb.get_web_window(module_name)
    window_width = frame_w * width_scale
    window_height = frame_h * height_scale
    web_window.webview.load(QUrl(url))
    web_window.loading_js_code = js_code
    web_window.resize(int(window_width), int(window_height))
    web_window.move(int(x), int(y))
    web_window.show()

def pop_translate_web(popweb, module_name, word):
    pop_url_window(popweb, module_name, 0, 0, 0, 0, 1900, 800, 0.35, 0.5, "https://www.youdao.com/w/eng/" + word, "")
