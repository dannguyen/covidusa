.DEFAULT_GOAL := build
.PHONY : clean help ALL wrangle build

help:
	@echo 'Run `make ALL` to see how things run from scratch'



ALL: collect build

build: fuse wrangle site


clean:
	@echo --- Cleaning derivations

site: datacopy

	cd jksite && bundle exec jekyll build --incremental
	rsync -arv --checksum jksite/_site/ docs


datacopy: wrangle

	# summaries
	cp backend/data/wrangled/state_summaries.json jksite/jdata/state_summaries.json
	# timeseries
	# cp backend/data/wrangled/timeseries.csv jksite/static/data/timeseries.csv

	# individual series
	cp -r backend/data/wrapped/series jksite/jdata/


wrap:
	./backend/scripts/wrap/wrap_state_series.py


wrangle: backend/data/wrangled/state_summaries.json backend/data/wrangled/timeseries.csv
	./backend/scripts/wrangle/wrangle_summary.py
	./backend/scripts/wrangle/wrangle_series.py

# backend/data/wrangled/state_summaries.json: backend/data/fused/jhcsse_normalized.csv

# backend/data/wrangled/timeseries.csv: backend/data/fused/jhcsse_normalized.csv


fuse: ./backend/data/fused/jhcsse_normalized.csv

data/fused/jhcsse_normalized.csv: backend/data/collected/jhcsse/timeseries_confirmed.csv backend/data/collected/jhcsse/timeseries_deaths.csv
	./backend/scripts/fuse_jhcsse_data.py

# ./backend/scripts/collect/collect_jhcsse_data.py

collect:
	./backend/scripts/collect/collect_covidtracking.py
	./backend/scripts/collect/collect_nytimes.py



