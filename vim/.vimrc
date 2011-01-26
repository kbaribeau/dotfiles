:syntax on

"search
set noincsearch
set nohlsearch
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

autocmd FileType * set tabstop=2|set shiftwidth=2|set noexpandtab
autocmd FileType java set tabstop=4|set shiftwidth=4|set expandtab

"turn off syntax folding unless we're in c#, where #regions are nice to have
set foldmethod=manual
autocmd FileType cs set foldmethod=syntax

"other
set nowrap
set showmode
set backspace=2
set nf="alpha, hex"
set scrolloff=3
set ruler

"put all temp files in the same directory
"set backupdir=~/.vim-tmp
"set directory=~/.vim-tmp

"bottom scrollbar / line numbers
set guioptions+=b

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


"code completion
autocmd FileType python set omnifunc=pythoncomplete#Complete
autocmd FileType javascript set omnifunc=javascriptcomplete#CompleteJS
autocmd FileType html set omnifunc=htmlcomplete#CompleteTags
autocmd FileType css set omnifunc=csscomplete#CompleteCSS
autocmd FileType xml set omnifunc=xmlcomplete#CompleteTags
autocmd FileType php set omnifunc=phpcomplete#CompletePHP
autocmd FileType c set omnifunc=ccomplete#Complete

set t_Co=256
set bg=dark
colo kbaribeau
