# MacPorts Installer addition on 2009-08-18_at_19:28:24: adding an appropriate PATH variable for use with MacPorts.
# -- moved PATHS to /etc/paths --kb
# Finished adapting your PATH environment variable for use with MacPorts.


# MacPorts Installer addition on 2009-08-18_at_19:28:24: adding an appropriate MANPATH variable for use with MacPorts.
export MANPATH=/opt/local/share/man:$MANPATH
# Finished adapting your MANPATH environment variable for use with MacPorts.

set +o vi -o emacs

#prompt
function parse_git_branch {
  ref=$(git symbolic-ref HEAD 2> /dev/null) || return
      echo "("${ref#refs/heads/}")"
}

export PS1="\w \$(parse_git_branch)\$ "

if [ -f ~/bin/hub ]; then
  alias git=~/bin/hub
fi

#ignore certain commands in history
HISTIGNORE="clear:bg:fg:jobs:cd:cd -:exit:date:w:* --help"

#more bash history
HISTSIZE=5000

YELLOWORANGE='\[\033[0;33m\]'
ORIG_FONT_COLOR='\[\033[0m\]'

export PS1=$YELLOWORANGE$PS1$ORIG_FONT_COLOR


#PATH stuff
if [ -e ~/bin ]; then
  export PATH=~/bin:$PATH
fi
export PATH=/usr/local/bin:/usr/local/sbin:$PATH
export PATH=/opt/local/libexec/git-core:$PATH
export PATH=/usr/local/mysql/bin:$PATH
export PATH=$PATH:/Users/kbaribeau/bin/datomic/current/bin
export PATH=$PATH:/Users/kbaribeau/bin/aws

export PATH="/usr/local/heroku/bin:$PATH" ### Added by the Heroku Toolbelt

export CDPATH=".:$HOME:$HOME/code"

export EDITOR=vim
export ANT_HOME=/usr/share/ant/
export ANT_OPTS="-Xms256M -Xmx512M"

alias 'be=bundle exec'
alias 'bs=bundle exec rspec'
alias 'ls=ls -G'
alias 'psg=ps ax | grep'
alias 'x=exit'
alias 'vm=if jobs | grep vim > /dev/null; then fg vim; else vim; fi'
alias 'rv=git show head > ~/patch.txt;git show origin/master > ~/patch_parent.txt' #for reviewboard
alias 'gg=git grep'
alias 'ggi=git grep -i'
alias 'gv=grep -v'
alias 'gi=grep -i'

#turn off mysql autocompletion. it makes startup too much slower
alias 'mysql=mysql -A'

#java
export MAVEN_OPTS=-Xmx1524m

#function to set window/tab title
function st {
 export PROMPT_COMMAND="echo -ne \"\033]0;$1\007\""
}

if [ -e ~/.profile.local ] ; then
  source ~/.profile.local
fi

#node
export PATH="node_modules/.bin:$PATH"

#python
export PATH=/Users/kbaribeau/.python_env/bin:$PATH

#rvm (do this last: rvm really wants to be the first thing in the path)
[[ -s $HOME/.rvm/scripts/rvm ]] && source $HOME/.rvm/scripts/rvm

#ruby git grep helpers
function ggd {
  git grep -iE "def.*$1"
}

function ggc {
  gg -iE "(class|module).*$1"
}

gg-files () { grep -E '.[a-zA-Z]{2,4}:' | cut -d : -f 1 | sort | uniq | xargs; }

shopt -s histappend
shopt -s extglob

#run this before using gvm
gvm-init () { [[ -s "/Users/kbaribeau/.gvm/bin/gvm-init.sh" ]] && source "/Users/kbaribeau/.gvm/bin/gvm-init.sh"; }

alias mvn_phudson='CATALINA_HOME=/Users/kbaribeau/tomcat mvn clean install -Phudson && mvn install -PjasmineDesktop && mvn install -PjasmineResponsive'

# source all homebrew-installed completion scripts
[[ -f $(brew --prefix)/etc/bash_completion ]] && source $(brew --prefix)/etc/bash_completion

. ~/.git-completion.bash

export NOMAD_ENV="dev"

alias tmux="TERM=screen-256color tmux"

#enable forward bash history search with C-s: http://stackoverflow.com/questions/791765/unable-to-forward-search-bash-history-similarly-as-with-ctrl-r
stty -ixon
complete -C aws_completer aws

#play midifiles with a soundfont + fluidsynth (brew install fluidsynth)
#stolen from: http://apple.stackexchange.com/questions/107297/how-can-i-play-a-midi-file-from-terminal
function playmidi {

    SOUNDFONT="/Users/kbaribeau/bin/generaluser.v.1.44.sf2"

    if [ -e "$SOUNDFONT" ]
    then

      for i in "$@"
      do
        if [ -e "$i" ]
        then
          (fluidsynth -i "$SOUNDFONT" "$i"  2>&1) >/dev/null
        else
          echo "[playmidi]: cannot find file at $i"
          return 1
        fi
      done
    else
      echo "[playmidi]: SOUNDFONT file not found at $SOUNDFONT"
      return 1
    fi
}

export PATH="$PATH:$HOME/.rvm/bin" # Add RVM to PATH for scripting
