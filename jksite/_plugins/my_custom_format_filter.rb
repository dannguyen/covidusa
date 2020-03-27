module Jekyll
  module MyCustomFormatFilter
    def short_date(dt)
      # assume dt is in YYYY-MM-DD format
      dx = Date.strptime(String(dt), '%Y-%m-%d')
      dx.strftime('%b %-d')
    end
  end
end

Liquid::Template.register_filter(Jekyll::MyCustomFormatFilter)
