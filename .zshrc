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

# Options: https://zsh.sourceforge.io/Doc/Release/Options.html#Description-of-Options

setopt prompt_subst
setopt INTERACTIVE_COMMENTS

# Get [] to work without escaping
unsetopt nomatch

# Can cause tab completion to be slow
unsetopt pathdirs

PROMPT='%~ $(parse_git_branch)\$ '
# PROMPT='
# %{$fg[magenta]%}%n%{$reset_color%} at %{$fg[yellow]%}%m%{$reset_color%} in %{$fg_bold[green]%}$(collapse_pwd)%{$reset_color%}$(hg_prompt_info)$(git_prompt_info)
# $(virtualenv_info)$(prompt_char) '

#ignore certain commands in history
HISTIGNORE="clear:bg:fg:jobs:cd:cd -:exit:date:w:* --help"

#more bash history
HISTSIZE=5000

export PROMPT="%F{yellow}$PROMPT%f"
export RPROMPT='%t'

# tab completion
autoload -Uz compinit && compinit

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
export PATH="/usr/local/opt/qt@5.5/bin:$PATH" # qt is installed with brew via a keg. This is for capybara-webkit

# export CDPATH=".:$HOME:$HOME/code" # causes tab completion to be slow

export EDITOR=vim
export ANT_HOME=/usr/share/ant/
export ANT_OPTS="-Xms256M -Xmx512M"

# Hendrick AWS
# export AWS_PROFILE=hendrick-legacy-aws

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
alias fixcam='sudo killall VDCAssistant' # fixes broken webcam on OSX

function hrc {
  # colorizing output in rails c can cause tmux(?) to slow down a lot. Have had problems with JSON output in rails c causing me to restart my tmux window
  heroku run 'rails c -- --nocolorize --noautocomplete' -a $1
}

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

#ruby git grep helpers
function ggd {
  git grep -iE "def.*$1"
}

function ggc {
  gg -E "(class|module).*$1"
}

gg-files () { grep -E '.[a-zA-Z]{2,4}:' | cut -d : -f 1 | sort | uniq | xargs; }


#run this before using gvm
gvm-init () { [[ -s "/Users/kbaribeau/.gvm/bin/gvm-init.sh" ]] && source "/Users/kbaribeau/.gvm/bin/gvm-init.sh"; }

export NOMAD_ENV="dev"

alias tmux="TERM=screen-256color tmux"

#enable forward bash history search with C-s: http://stackoverflow.com/questions/791765/unable-to-forward-search-bash-history-similarly-as-with-ctrl-r
stty -ixon

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

if [ -d $HOME/.rbenv ]
then
  export PATH="$HOME/.rbenv/bin:$PATH"
  eval "$(rbenv init -)"
fi

# Disable spring because of issues with fsevent_watch (https://github.com/rails/rails/issues/26158)
export DISABLE_SPRING=1

export PATH="$HOME/.cargo/bin:$PATH"

ulimit -n 4096

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

# Change node versions with nvm based on .nvmrc files
autoload -U add-zsh-hook
load-nvmrc() {
  local node_version="$(nvm version)"
  local nvmrc_path="$(nvm_find_nvmrc)"

  if [ -n "$nvmrc_path" ]; then
    local nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

    if [ "$nvmrc_node_version" = "N/A" ]; then
      nvm install
    elif [ "$nvmrc_node_version" != "$node_version" ]; then
      nvm use
    fi
  elif [ "$node_version" != "$(nvm version default)" ]; then
    echo "Reverting to nvm default version"
    nvm use default
  fi
}
add-zsh-hook chpwd load-nvmrc
load-nvmrc

psls () {
  PERSONALYSIS_PATH="/Users/kbaribeau/Personalysis - All Employees"
  file_name=`ls -1 $PERSONALYSIS_PATH | grep -i "$1" | head -n 1`
  open "$PERSONALYSIS_PATH/$file_name"
}

export PUMA_DEBUG=1

# This is slow?
# export DOCKER_DEFAULT_PLATFORM=linux/amd64
# export DOCKER_DEFAULT_PLATFORM=linux/arm64 # doesn't work?
