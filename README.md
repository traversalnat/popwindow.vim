# popwindow.vim
a vim version popweb (https://github.com/manateelazycat/popweb.git)

1. Install PyQt6 `pip install PyQt6 PyQt6-Qt6 PyQt6-sip PyQt6-WebEngine PyQt6-WebEngine-Qt6`
2. Install werkzeug and json-rpc`pip install werkzeug json-rpc`

In .vimrc
```
autocmd VimEnter * call web#start_server()
nmap <leader>b : call youdao#web() <CR>
vnoremap <silent> <Plug>VMkdown :<C-U>call markdown#web() <CR>
xmap B   <Plug>VMkdown
```
