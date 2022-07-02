from PyQt6.QtCore import QUrl
import os

def pop_md_window(popweb, module_name, x, y, frame_x, frame_y, frame_w, frame_h, width_scale, height_scale, index_file, md_string):
    web_window = popweb.get_web_window(module_name)
    window_width = frame_w * width_scale
    window_height = frame_h * height_scale
    web_window.loading_js_code = ""
    index_html = open(index_file, "r").read().replace("INDEX_DIR", os.path.dirname(index_file)).replace("MARKDOWN", md_string)
    web_window.webview.setHtml(index_html, QUrl("file://"))
    web_window.resize(int(window_width), int(window_height))
    web_window.move(int(x), int(y))
    web_window.show()
