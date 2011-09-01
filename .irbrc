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
		Wirble::Colorize.colors.merge!(
      :string => :light_purple,
      :comma => :white,
      :open_hash => :white,
      :close_hash => :white,
      :open_array => :white,
      :close_array => :white,
      :symbol => :light_purple,
      :symbol_prefix => :light_purple,
      :open_string => :white,
      :close_string => :white,
      :number => :white,
      :keyword => :cyan,
      :class => :cyan,
      :range => :light_purple
    )
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



