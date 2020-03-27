module Jekyll
  module SpecialPathsFilter
    def single_series_json_path(id)
      "static/data/series/#{id}.json"
    end
  end
end

Liquid::Template.register_filter(Jekyll::SpecialPathsFilter)
