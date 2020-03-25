.DEFAULT_GOAL := help
.PHONY : clean help ALL wrangle build

help:
	@echo 'Run `make ALL` to see how things run from scratch'

ALL: collect fuse wrangle site


clean:
	@echo --- Cleaning derivations

site: datacopy

	cd jksite && bundle exec jekyll build --incremental
	rsync -arv --checksum jksite/_site/ docs


datacopy: wrangle

	# summaries
	cp data/wrangled/state_summaries.json jksite/_data/state_summaries.json
	cp data/wrangled/state_summaries.json jksite/static/data/state_summaries.json
	# timeseries
	cp data/wrangled/timeseries.csv jksite/static/data/timeseries.csv



wrangle: data/wrangled/state_summaries.json data/wrangled/timeseries.csv

data/wrangled/state_summaries.json: data/fused/jhcsse_normalized.csv
	./scripts/wrangle_summary.py

data/wrangled/timeseries.csv: data/fused/jhcsse_normalized.csv
	./scripts/wrangle_timeseries.py


fuse: data/fused/jhcsse_normalized.csv

data/fused/jhcsse_normalized.csv: data/collected/jhcsse/timeseries_confirmed.csv data/collected/jhcsse/timeseries_deaths.csv
	./scripts/fuse_jhcsse_data.py

collect:
	./scripts/collect_jhcsse_data.py
	./scripts/collect_covidtracking.py



