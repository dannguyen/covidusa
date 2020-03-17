# covid19-change-tracker


Data courtesy of the daily snapshots from [Johns Hopkins Center for Systems Science and Engineering](https://systems.jhu.edu/research/public-health/ncov/)

https://github.com/CSSEGISandData/COVID-19

- Timeseries confirmed: https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv
- Timeseries deaths: https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv
- Daily reports: https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/03-16-2020.csv


## Other good trackers
- https://www.washingtonpost.com/graphics/2020/world/mapping-spread-new-coronavirus/
- JH's Desktop tracker: https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6
- https://ncov2019.live/data
- https://covidtracking.com/
- https://www.bloomberg.com/graphics/2020-wuhan-novel-coronavirus-outbreak/
- https://www.livescience.com/coronavirus-updates-united-states.html
- https://www.cnn.com/2020/03/03/health/us-coronavirus-cases-state-by-state/index.html
- https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html

## TODO

- rename lookups/us_states.csv to lookups/fips.csv
- wrangle places.csv
- wrangle us_state_counts
- wrangle country_counts for main countries: iran, china, south_korea, italy, canada, mexico, uk
- optionally: make a us_cities count 
- wrangle fields should be:
    - state, name, fips, current_day_confirmed, current_day_deaths, yesterday_confirmed, previous_7days_confirmed, previous_14days_confirmed, date_first_confirmed

- wrangler makes a JSON!

- get census counts


### data insights

- For each state, show:
    - infections per capita
    - earliest infection
    - day to day change
    - weekly change
    - 14 day change


- D3
    - load csv, show basic numbers
    - Make data table listing each state

- Svelte
    - Make state endpoints/click events
    - get state shapefiles


# make a separate front-end site? (nah)



# state event metadata

https://docs.google.com/spreadsheets/d/1De8fx-nM2Dlmhy38oYlKimB3ug03wjGopqifJXYR_-w/edit?usp=sharing
