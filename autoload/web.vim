let s:path = expand("<sfile>:p:h")

function! <SID>translate(word)

let saved_pos = getcurpos()

if has('python3')
py3 << EOF
import vim
import os
import sys
import requests
import json

sys.path.append(vim.eval("s:path"))

js_code = """window.scrollTo(0, 0); document.getElementsByTagName('html')[0].style.visibility = 'hidden'; document.getElementById('results').style.visibility = 'visible'; document.getElementById('scontainer').style.margin = '0'; document.getElementById('scontainer').style.padding = '0'; document.getElementById('result_navigator').style.display = 'none'; document.getElementById('container').style.padding = '0'; document.getElementById('container').style.paddingLeft = '10px'; document.getElementById('container').style.margin = '0'; document.getElementById('topImgAd').style.display = 'none';"""

url = "http://localhost:4000/jsonrpc"

module_path = vim.eval("s:path") + "/pop_url_window.py"

word = vim.eval("a:word")

pos = vim.eval("getwinpos()")
x, y = int(pos[0]), int(pos[1]) + 20

# y = vim.current.window.col

payload = {
  "method": "call_module_method",
  "params": [module_path,
      "pop_url_window", ["bing_translate", x, y, 0, 0, 1900, 800, 0.35, 0.5, "https://www.youdao.com/w/eng/" + word, js_code]
      ],
  "jsonrpc": "2.0",
  "id": 0,
}

requests.post(url, json=payload).json()

EOF
endif

" any key input will hide the window
let in = getchar()

call <SID>hideWindow()

endfunction

function! <SID>hideWindow()
if has('python3')
py3 << EOF
import vim
import os
import sys
import requests
import json

url = "http://localhost:4000/jsonrpc"

payload = {
  "method": "hide_web_window",
  "params": [
      "bing_translate"
      ],
  "jsonrpc": "2.0",
  "id": 0,
}

requests.post(url, json=payload).json()

EOF
endif
endfunction

function! web#bing()
	let word = expand("<cword>")
    call <SID>translate(word)
endfunction

function! web#bingClose()
    call <SID>hideWindow()
endfunction
