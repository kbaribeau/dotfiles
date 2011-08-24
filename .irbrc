class WirableConfig

	def run() 
		change_wirable_colors_to_look_vaguely_like_my_vim()

		wirble_opts = {
			:skip_prompt => true,
			:skip_shortcuts => true,
			:init_colors => true,
		}

		Wirble.init(wirble_opts)
	end


	def change_wirable_colors_to_look_vaguely_like_my_vim()
		Wirble::Colorize.colors[:string] = :light_purple

		Wirble::Colorize.colors[:comma] = :white

		Wirble::Colorize.colors[:open_hash] = :white
		Wirble::Colorize.colors[:close_hash] = :white

		Wirble::Colorize.colors[:open_array] = :white
		Wirble::Colorize.colors[:close_array] = :white

		Wirble::Colorize.colors[:symbol] = :light_purple
		Wirble::Colorize.colors[:symbol_prefix] = :light_purple

		Wirble::Colorize.colors[:open_string] = :white
		Wirble::Colorize.colors[:close_string] = :white

		Wirble::Colorize.colors[:number] = :white
		Wirble::Colorize.colors[:keyword] = :cyan
		Wirble::Colorize.colors[:class] = :cyan
		Wirble::Colorize.colors[:range] = :light_purple
	end
end

begin
  require 'rubygems' rescue nil
  require 'wirble'

  config = WirableConfig.new()
  config.run()
rescue LoadError
  nil
end



