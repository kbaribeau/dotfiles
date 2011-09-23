let g:CommandTMaxHeight=25

call pathogen#runtime_append_all_bundles()

filetype plugin indent on
syntax on

"colors
set bg=dark
"let g:solarized_visibility = 'low'
set t_Co=256
colo calmar256-dark

"search
set incsearch
set nohlsearch
nnoremap <return> :set hls!<return><return>

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
set nolist
set cursorline
set autoread

set winwidth=120

nnoremap <c-j> <c-w>j
nnoremap <c-k> <c-w>k
nnoremap <c-h> <c-w>h
nnoremap <c-l> <c-w>l

 "I only ever hit this by accident
:map K <Nop>

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
map <C-Right> :tabn<cr>
map <C-Left> :tabp<cr>

"turn off the bell
set vb
set t_vb=

"leader key for plugins
let mapleader = "\\"
map <leader><leader> <C-^>

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

" Show syntax highlighting groups for word under cursor
function! SynStack()
  if !exists("*synstack")
    return
  endif
  echo map(synstack(line('.'), col('.')), 'synIDattr(v:val, "name")')
endfunc
map <leader>ss :call SynStack()<CR>

"execute :GitGrep for word under cursor
map <leader>gg :GitGrep <C-R>=expand("<cword>")<cr><cr><C-w>p<C-o><C-w>p

"command-T mappings
map <leader>gv :CommandTFlush<cr>\|:CommandT app/views<cr>
map <leader>gc :CommandTFlush<cr>\|:CommandT app/controllers<cr>
map <leader>gm :CommandTFlush<cr>\|:CommandT app/models<cr>
map <leader>gh :CommandTFlush<cr>\|:CommandT app/helpers<cr>
map <leader>gl :CommandTFlush<cr>\|:CommandT lib<cr>
map <leader>gp :CommandTFlush<cr>\|:CommandT public<cr>
map <leader>gs :CommandTFlush<cr>\|:CommandT public/stylesheets/sass<cr>
map <leader>gt :CommandTFlush<cr>\|:CommandT spec/<cr>

cnoremap %% <C-R>=expand('%:h').'/'<cr>
map <leader>e :edit %%
map <leader>v :view %%

"prevent nerdtree from overriding netrw. I only have nerdtree installed in case my pair really wants it
let g:NERDTreeHijackNetrw = 0
map <leader>n :NERDTreeToggle<cr>

"clojure
let vimclojure#ParenRainbow=1

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

iabbr rdebug require 'ruby-debug'; debugger
iabbr cljpp [clojure.pprint :only [pprint]]

if has("ruby_fold")
	ruby_fold=
endif
autocmd BufRead,BufNewFIle *.rb :silent exe "g:flog_enable"

"auto reload vimrc when saving it
autocmd! BufWritePost .vimrc,vimrc source $MYVIMRC

if filereadable(expand('~/.vimrc.local'))
  source ~/.vimrc.local
endif
