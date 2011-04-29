let g:CommandTMaxHeight=25

call pathogen#runtime_append_all_bundles() 

filetype plugin indent on
syntax on

"colors
set bg=dark
colo solarized

"search
set incsearch
set hlsearch
nnoremap <return> :noh<return><esc><return>

set ignorecase
set smartcase
set magic

"indent and tabs
set autoindent
set smartindent
set softtabstop=0
set shiftwidth=2
set tabstop=2
set shiftround

set expandtab

"other
set nowrap
set showmode
set backspace=2
set nf="alpha, hex"
set scrolloff=3
set ruler
set number

"put all temp files in the same directory
"set backupdir=~/.vim-tmp
"set directory=~/.vim-tmp

"extended % functionality
runtime macros/matchit.vim

"show statusline
set laststatus=2
"this looks like the default statusline, but with git info embedded, thanks to vim-fugitive
set statusline=%<%f%{fugitive#statusline()}\ %h%m%r%=%-14.(%l,%c%V%)\ %P

"maps
:map <C-Right> :tabn<cr>
:map <C-Left> :tabp<cr>

"turn off the bell
set vb
set t_vb=

"leader key for plugins
let mapleader = "\\"

"stolen from @garybernhardt
function! RenameFile()
    let old_name = expand('%')
    let new_name = input('New file name: ', expand('%'))
    if new_name != '' && new_name != old_name
        exec ':saveas ' . new_name
        exec ':silent !rm ' . old_name
        redraw!
    endif
endfunction
map <leader>rn :call RenameFile()<cr>

"<leader>g -> execute :GitGrep for word under cursor
map <leader>g :GitGrep <C-R>=expand("<cword>")<cr><cr><C-w>p<C-o><C-w>p

"prevent nerdtree from overriding netrw. I only have nerdtree installed in case my pair really wants it
let g:NERDTreeHijackNetrw = 0

"clojure
let vimclojure#ParenRainbow=1
autocmd FileType clojure AutoCloseOff

"code completion
autocmd FileType python set omnifunc=pythoncomplete#Complete
autocmd FileType javascript set omnifunc=javascriptcomplete#CompleteJS
autocmd FileType html set omnifunc=htmlcomplete#CompleteTags
autocmd FileType css set omnifunc=csscomplete#CompleteCSS
autocmd FileType xml set omnifunc=xmlcomplete#CompleteTags
autocmd FileType php set omnifunc=phpcomplete#CompletePHP
autocmd FileType c set omnifunc=ccomplete#Complete

"parse *.prawn as ruby
autocmd BufRead,BufNewFile *.prawn setfiletype ruby

if has("ruby_fold")
	ruby_fold=
endif
:silent exe "g:flog_enable"

