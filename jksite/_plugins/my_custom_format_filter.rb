module Jekyll
  module MyCustomFormatFilter
    MONTH_ABBRS = [
      'N/A',
      'Jan.',
      'Feb.',
      'March',
      'April',
      'May',
      'June',
      'July',
      'Aug.',
      'Sept.',
      'Oct.',
      'Nov.',
      'Dec.',
    ]

    def short_date(dt)
      # assume dt is in YYYY-MM-DD format
      dx = Date.strptime(String(dt), '%Y-%m-%d')

      return "#{MONTH_ABBRS[dx.month]} #{dx.day}"
    end
  end
end

Liquid::Template.register_filter(Jekyll::MyCustomFormatFilter)
