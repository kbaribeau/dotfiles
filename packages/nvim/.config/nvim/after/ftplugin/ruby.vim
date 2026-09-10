" Preserve the inserted text, not a promise that each project's debugger API exists.
" In particular, legacy byebug requires debug but still calls byebug.
inoreabbrev <buffer> rdebug require 'ruby-debug'; debugger; puts "debugger should stop here"
inoreabbrev <buffer> rpry require 'pry'; binding.pry; puts "debugger should stop here"
inoreabbrev <buffer> byebug require 'debug'; byebug; puts 'debugger should stop here'
inoreabbrev <buffer> debug require "debug"; binding.break; puts "debugger should stop here"
let b:undo_ftplugin = get(b:, 'undo_ftplugin', '') . (exists('b:undo_ftplugin') ? ' | ' : '')
      \ . 'silent! iunabbrev <buffer> rdebug | silent! iunabbrev <buffer> rpry | silent! iunabbrev <buffer> byebug | silent! iunabbrev <buffer> debug'
