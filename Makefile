.DEFAULT_GOAL := build
.PHONY : clean help ALL wrangle build

help:
	@echo 'Run `make ALL` to see how things run from scratch'



ALL: collect build

build: fuse wrap site


clean:
	@echo --- Cleaning derivations

site: datacopy

	cd jksite && bundle exec jekyll build --incremental
	rsync -arv --checksum jksite/_site/ docs


datacopy:

	# summaries
	cp backend/data/wrapped/summary.json jksite/jdata/summary.json
	# individual series
	cp -r backend/data/wrapped/series jksite/jdata/


wrap: wrangle
	./backend/scripts/wrap/wrap_state_series.py
	./backend/scripts/wrap/wrap_summary.py



wrangle: ./backend/data/wrangled/us-series.csv

./backend/data/wrangled/us-series.csv: ./backend/data/fused/nytimes-us.csv

	./backend/scripts/wrangle/wrangle_covid_series.py



fuse: ./backend/data/fused/nytimes-us.csv

./backend/data/fused/nytimes-us.csv: data/collected/nytimes/us-counties.csv data/collected/nytimes/us-states.csv

	./backend/scripts/fuse/fuse_nytimes.py


collect: collect_nyt data/collected/covidtracking

collect_nyt: data/collected/nytimes/us-counties.csv data/collected/nytimes/us-states.csv


data/collected/nytimes/us-counties.csv:

	./backend/scripts/collect/collect_nytimes.py

data/collected/nytimes/us-states.csv: data/collected/nytimes/us-counties.csv

    $(NOECHO) $(NOOP)


data/collected/covidtracking/:

	./backend/scripts/collect/collect_covidtracking.py




