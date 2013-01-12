
filetype off " must be disabled while we configure vundle

set rtp+=~/.vim/bundle/vundle/
call vundle#rc()

"required
Bundle 'gmarik/vundle'

"github
  Bundle 'tpope/vim-fugitive'
  Bundle 'tpope/vim-cucumber'
  Bundle 'tpope/vim-endwise'
  Bundle 'tpope/vim-surround'
  Bundle 'tjennings/git-grep-vim'
  Bundle 'nathanaelkane/vim-indent-guides'
  Bundle 'kchmck/vim-coffee-script'
  Bundle 'pangloss/vim-javascript'

"vimscripts

  Bundle 'Align'
  Bundle 'vim-indent-object'
  Bundle 'mru.vim'
  Bundle 'SuperTab'

  Bundle 'VimClojure'
  let vimclojure#ParenRainbow=1


"non github
  Bundle 'git://git.wincent.com/command-t.git'
  let g:CommandTMaxHeight=25
  map <leader>gv :CommandTFlush<cr>\|:CommandT app/views<cr>
  map <leader>gc :CommandTFlush<cr>\|:CommandT app/controllers<cr>
  map <leader>gm :CommandTFlush<cr>\|:CommandT app/models<cr>
  map <leader>gh :CommandTFlush<cr>\|:CommandT app/helpers<cr>
  map <leader>gl :CommandTFlush<cr>\|:CommandT lib<cr>
  map <leader>gp :CommandTFlush<cr>\|:CommandT public<cr>
  map <leader>gs :CommandTFlush<cr>\|:CommandT public/stylesheets/sass<cr>
  map <leader>gt :CommandTFlush<cr>\|:CommandT spec/<cr>


"autocmd BufWritePost plugins.vim source ~/.vim/plugins.vim
filetype plugin indent on
