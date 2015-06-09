source ~/.vim/plugins.vim

syntax on

"colors

set bg=dark
set t_Co=256
colo grb256

"search
set hlsearch

"display '.' and '..' in netrw
let g:netrw_list_hide = ',\~$,^tags$'


set ignorecase
set magic

"indent and tabs
set softtabstop=0
set shiftwidth=2
set tabstop=2

set expandtab

"other
set nowrap
set showmode
set nf="alpha, hex"
set scrolloff=3 "overridden from vim-sensible
set number
set list
set cursorline "turning this on makes things slow, but I'll try not to care
"set clipboard=unnamed "use system clipboard

set winwidth=120

nnoremap <c-j> <c-w>j
nnoremap <c-k> <c-w>k
nnoremap <c-h> <c-w>h
nnoremap <c-l> <c-w>l

nnoremap  <F1> <Esc>

"autosave when I suspend vim(I do this a lot)
:noremap <C-Z> :wa<CR><C-Z>
:inoremap <C-Z> <Esc>:wa<CR><C-Z>

 "I only ever hit this by accident
:map K <Nop>

"let's try running without backup for awhile, just to see if I regret it
set nobackup
set nowritebackup
"if you ever turn backups back on, uncomment this next line
"au! BufNewFile,BufRead crontab.* set nobackup | set nowritebackup

set undodir=~/.vim/undo
set undofile
set backupdir=~/.vim/backups
set dir=~/.vim/swap

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

"virtual whitespace
set virtualedit+=block
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

cnoremap %% <C-R>=expand('%:h').'/'<cr>
map <leader>e :edit %%
map <leader>v :view %%

"clojure
iabbr cljpp [clojure.pprint :only [pprint]]

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

autocmd FileType js set foldmethod=manual

"ruby specific stuff
iabbr rdebug require 'ruby-debug'; debugger; puts "debugger should stop here"
iabbr rpry require 'pry'; binding.pry; puts "debugger should stop here"

let ruby_space_errors = 1
if has("ruby_fold")
	ruby_fold=
endif

" Allow saving of files as sudo when I forgot to start vim using sudo.
cmap w!! w !sudo tee > /dev/null %

"auto reload vimrc when saving it
autocmd! BufWritePost .vimrc,vimrc source $MYVIMRC

"vim can be slow when dealing with large xml files
"turn some stuff off so it's not so bad
"maybe I should turn this on for large files in general? meh.
function! SynOffForLargeFiles()
  if line('$') > 1000
    syn off
    set nocursorline
  endif
endfunction
autocmd FileType xml :call SynOffForLargeFiles()

"jump to last cursor position unless it's invalid or in an event handler
"(see :help line)"
:au BufReadPost *
  \ if line("'\"") > 1 && line("'\"") <= line("$") |
  \   exe "normal! g`\"" |
  \ endif

if filereadable(expand('~/.vimrc.local'))
  source ~/.vimrc.local
endif

" Run a given vim command on the results of fuzzy selecting from a given shell
" command. See usage below.
function! SelectaCommand(choice_command, selecta_args, vim_command)
  try
    let selection = system(a:choice_command . " | selecta " . a:selecta_args)
  catch /Vim:Interrupt/
    " Swallow the ^C so that the redraw below happens; otherwise there will be
    " leftovers from selecta on the screen
    redraw!
    return
  endtry
  redraw!
  exec a:vim_command . " " . selection
endfunction

" Find all files in all non-dot directories starting in the working directory.
" Fuzzy select one of those. Open the selected file with :e.
nnoremap <leader>f :call SelectaCommand("find * -type f", "", ":e")<cr>

"rainbow parens
au VimEnter * RainbowParenthesesToggle
au Syntax * RainbowParenthesesLoadRound
au Syntax * RainbowParenthesesLoadSquare
au Syntax * RainbowParenthesesLoadBraces
