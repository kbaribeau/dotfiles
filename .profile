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

if [ -f ~/bin/hub ]; then
  alias git=~/bin/hub
fi

export PS1="\w \$(parse_git_branch)\$ "

#ignore certain commands in history
HISTIGNORE="clear:bg:fg:cd:cd -:exit:date:w:* --help"

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

if [ -e /opt/groovy-1.7.3 ]; then
  export PATH=/opt/groovy-1.7.3/bin:/opt/grails-1.3.1/bin:$PATH
  export GRAILS_HOME=/opt/grails-1.3.1
fi

export EDITOR=vim
export ANT_HOME=/usr/share/ant/
export ANT_OPTS="-Xms256M -Xmx512M"

alias 'be=bundle exec'
alias 'bs=bundle exec spec'
alias 'ls=ls -G'
alias 'psg=ps ax | grep'
alias 'x=exit'
alias 'vm=if jobs | grep vim > /dev/null; then fg vim; else vim; fi'
alias 'rv=git show head > ~/patch.txt;git show origin/master > ~/patch_parent.txt' #for reviewboard

#http://github.com/rupa/z
. ~/code/dotfiles/z.sh

#java
export MAVEN_OPTS=-Xmx1524m

#ruby (ree)
export RUBY_HEAP_MIN_SLOTS=500000
export RUBY_HEAP_SLOTS_INCREMENT=250000
export RUBY_HEAP_SLOTS_GROWTH_FACTOR=1
export RUBY_GC_MALLOC_LIMIT=50000000

#function to set window/tab title
function st {
 export PROMPT_COMMAND="echo -ne \"\033]0;$1\007\""
}

#autoexpand ! commands when I press spacebar
bind Space:magic-space

#rvm
[[ -s $HOME/.rvm/scripts/rvm ]] && source $HOME/.rvm/scripts/rvm

if [ -e ~/.profile.local ] ; then
  source ~/.profile.local
fi
