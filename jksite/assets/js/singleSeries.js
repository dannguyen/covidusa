---
# hi
---

;
var qx = 1, zx =1;

var DATA_URL = "{{ '/static/data/timeseries.csv?v=' | append: site.github.build_revision | relative_url }}"




function renderSeriesChart(svgId, abbr){
    var svg = d3.select('#'+svgId),
        width = svg.node().getBoundingClientRect().width,
        height = svg.node().getBoundingClientRect().height;


    console.log("width: ", width, "height: ", height)



    var seriesPromise = d3.csv(DATA_URL, function(d){
        return {id: d.id, date: new Date(d.date), confirmed: +d.confirmed, deaths: +d.deaths}
    });


    Promise.all([seriesPromise])
        .then(function(the_response){
            zx = the_response[0]
            var sdata = qx = the_response[0].filter(function(n){ return n['id'] == abbr})

            var xScale = d3.scaleTime().range([0, width]);
            xScale.domain(d3.extent(sdata, function(d){ return d.date }))
            var yScale = d3.scaleLinear().range([height, 0]);
            yScale.domain([0, d3.max(sdata, function(d){ return d.confirmed })])


            var dline = d3.line()
                .x(function(d){ return xScale(d.date)})
                .y(function(d){ return yScale(d.confirmed)})
                .curve(d3.curveMonotoneX);

            svg.append("path")
                .datum(sdata)
                .attr("class", "line")
                .attr("d", dline)

    });

}
