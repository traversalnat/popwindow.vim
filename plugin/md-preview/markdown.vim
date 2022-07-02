let s:path = expand("<sfile>:p:h")

function! <SID>markdown(md_text)
if has('python3')
py3 << EOF
import vim
import os
import sys
import requests
import json
url = "http://localhost:4000/jsonrpc"

module_path = vim.eval("s:path") + "/pop_md_window.py"
index_file = vim.eval("s:path") + "/md.html"
md_text = vim.eval("a:md_text").replace("\n", "\\n").replace('"', '\\"')

pos = vim.eval("getwinpos()")
x, y = int(pos[0]), int(pos[1]) + 20

payload = {
  "method": "call_module_method",
  "params": [module_path,
      "pop_md_window", ["markdown", x, y, 0, 0, 1900, 800, 0.35, 0.5, index_file, md_text]
      ],
  "jsonrpc": "2.0",
  "id": 0,
}

try:
    requests.post(url, json=payload)
except:
    print("Use WebStart to webWindow server")

EOF
endif

" any key input will hide the window
let in = getchar()
call feedkeys(nr2char(in))

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
      "markdown"
      ],
  "jsonrpc": "2.0",
  "id": 0,
}

try:
    requests.post(url, json=payload).json()
except:
    pass

EOF
endif
endfunction

function! markdown#web()
	let md_text = expand("<cword>")
	try
		let a_save = @a
		" 将visual 模式选中的字符串保存到寄存器 a
		silent normal! gv"ay
		let md_text = @a
	finally
		" 使用完寄存器后恢复寄存器
		let @a = a_save
	endtry

    call <SID>markdown(md_text)
endfunction

function! markdown#hide()
    if !web#server_started()
        return
    endif
    call <SID>hideWindow()
endfunction
