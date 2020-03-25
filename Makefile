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




collect:
	./scripts/collect_jhcsse_data.py

fuse:
	./scripts/fuse_jhcsse_data.py

wrangle: data/wrangled/state_summaries.json data/wrangled/timeseries.csv

data/wrangled/state_summaries.json:
	./scripts/wrangle_summary.py

data/wrangled/timeseries.csv:
	./scripts/wrangle_timeseries.py
