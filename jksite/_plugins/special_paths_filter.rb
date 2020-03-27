module Jekyll
  module SpecialPathsFilter
    def single_series_json_path(id)
      "jdata/series/#{id}.json"
    end
  end
end

Liquid::Template.register_filter(Jekyll::SpecialPathsFilter)
