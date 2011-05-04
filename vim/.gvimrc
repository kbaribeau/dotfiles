" Unmap Apple+S to remap to Esc, then :w<CR>
macmenu &File.Save key=<nop>
imap <D-s> <Esc>:w<CR>
map <D-s> :w<CR>

" TABS: safari style tab navigation
nmap <D-[> :tabprevious<CR>
nmap <D-]> :tabnext<CR>
map <D-[> :tabprevious<CR>
map <D-]> :tabnext<CR>
imap <D-[> <C-O>:tabprevious<CR>
imap <D-]> <C-O>:tabnext<CR>

" TABS: Firefox style, open tabs with command-<tab number>
map <silent> <D-1> :tabn 1<CR>
map <silent> <D-2> :tabn 2<CR>
map <silent> <D-3> :tabn 3<CR>
map <silent> <D-4> :tabn 4<CR>
map <silent> <D-5> :tabn 5<CR>
map <silent> <D-6> :tabn 6<CR>
map <silent> <D-7> :tabn 7<CR>
map <silent> <D-8> :tabn 8<CR>
map <silent> <D-9> :tabn 9<CR>

"fullscreen expands vim window
set fuoptions=maxvert,maxhorz

set guioptions=e

"auto reload gvimrc when saving
autocmd! BufWritePost .gvimrc,gvimrc source $MYGVIMRC
autocmd! BufWritePost .vimrc,vimrc source $MYVIMRC | source $MYGVIMRC
