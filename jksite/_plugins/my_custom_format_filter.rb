require 'active_support'
module ActS
    extend ActiveSupport::NumberHelper
end


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

    def number_with_delimiter(number)
      ActS.number_to_delimited(number)
    end

    def number_as_pct(number, precision=1)
      ActS.number_to_percentage(number, precision: precision)
    end

  end
end

Liquid::Template.register_filter(Jekyll::MyCustomFormatFilter)
