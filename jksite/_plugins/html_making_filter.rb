module Jekyll
  module HtmlMakingFilter
    # dtk: deprecated
    def delta_value(val, number=nil)
      number = number.blank? ? val : number
      if number > 0
        sign_class = 'positive'
      elsif number < 0
        sign_class= 'negative'
      else
        sign_class = 'zero'
      end

      %Q{<span class="delta #{sign_class}" data-value="#{number}">
        #{val}
        </span>}
    end
  end
end

Liquid::Template.register_filter(Jekyll::HtmlMakingFilter)
