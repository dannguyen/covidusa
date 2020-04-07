module Jekyll
  module SpecialPathsFilter
    # dtk: deprecated
    def entity_json_path(id)
      "jdata/entities/#{id}.json"
    end
  end
end

Liquid::Template.register_filter(Jekyll::SpecialPathsFilter)
