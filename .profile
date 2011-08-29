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

##
# Your previous /Users/kbaribeau/.profile file was backed up as /Users/kbaribeau/.profile.macports-saved_2009-10-13_at_21:59:12
##

export PATH="$HOME/bin:/usr/local/bin:/usr/local/sbin:$PATH"
 
# Finished adapting your PATH environment variable for use with MacPorts.

#add git-svn to PATH
export PATH=/opt/local/libexec/git-core:$PATH
#add mysql
export PATH=/usr/local/mysql/bin:$PATH

#add groovy/grails to path
export PATH=/opt/groovy-1.7.3/bin:/opt/grails-1.3.1/bin:$PATH

#grails env
export GRAILS_HOME=/opt/grails-1.3.1

export EDITOR=vim
export ANT_HOME=/usr/share/ant/
export ANT_OPTS="-Xms256M -Xmx512M"

#gale stuff
export JBOSS_HOME="/Users/kbaribeau/apps/jboss-portal-2.7.2"
export CATALINA_HOME="/Users/kbaribeau/apps/apache-tomcat-5.5.28"
export environment="local"
JAVA_OPTS="-Denvironment=local"

alias 'be=bundle exec'
alias 'ls=ls -G'
alias 'psg=ps ax | grep'
alias 'x=exit'

#http://github.com/rupa/z
. ~/code/dotfiles/z.sh

#java
export MAVEN_OPTS=-Xmx1524m

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
