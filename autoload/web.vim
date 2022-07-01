let s:path = expand("<sfile>:p:h")
let s:server_path = v:none

function! web#start_server()
if web#server_started()
    return
endif
let s:server_path = s:path . "/webWindow.py"
if has('python3')
py3 << EOF
from subprocess import Popen

Popen("python3 " + vim.eval("s:server_path") + " >&2 2>/dev/null", shell=True)

EOF
endif
endfunction

function! web#stop_server()
    " TODO 停止 webWindow 进程, 能不能得到另一个函数中的变量?
endfunction

function! web#server_started()
if has('python3')
py3 << EOF
import socket
sock = socket.socket()
binded = 0
try:
    sock.bind(("0.0.0.0", 4000))
except:
    binded = 1 
sock.close()
vim.command("let l:binded = " + str(binded))
EOF
return l:binded
endif
endfunction

autocmd VimEnter * call web#start_server()
command! -nargs=0 WebStart  :call web#start_server()
command! -nargs=0 WebStop   :call web#stop_server()
