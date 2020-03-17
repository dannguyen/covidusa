.DEFAULT_GOAL := help
.PHONY : clean help ALL wrangle build

SQLIZED_DB = data/myfoo.sqlite
STUB_WRANGLED = data/wrangled/helloworld.csv
STUB_COLLATED = data/collated/helloworld.csv
STUB_STASHED = data/stashed/hello.txt \
			   data/stashed/world.txt

help:
	@echo 'Run `make ALL` to see how things run from scratch'

ALL: collect fuse wrangle site


site: data/wrangled/state_summaries.json

	cp data/wrangled/state_summaries.json jekyllsite/_data/state_summaries.json
	cd jekyllsite && bundle exec jekyll build --incremental
	rsync -arv --checksum jekyllsite/_site/ docs


clean:
	@echo --- Cleaning derivations


collect:
	./scripts/collect_jhcsse_data.py

fuse:
	./scripts/fuse_jhcsse_data.py

wrangle: data/wrangled/state_summaries.json

data/wrangled/state_summaries.json:
	./scripts/wrangle.py

