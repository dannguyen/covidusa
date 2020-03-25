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
            var sdata = qx = the_response[0].filter(function(d){ return d.id== abbr && d.confirmed > 0})

            var xScale = d3.scaleTime()
                            .domain(d3.extent(sdata, function(d){ return d.date }))
                            .range([0, width])

            var yScale = d3.scaleLog()
                            .domain([1, d3.max(sdata, function(d){ return d.confirmed })])
                            .range([height, 0])

            var dline = d3.line()
                .x(function(d){ return xScale(d.date)})
                .y(function(d){ return yScale(d.confirmed)})
                .curve(d3.curveMonotoneX);

            svg.append("path")
                .datum(sdata)
                .attr("class", "line")
                .attr("d", dline)
            // add dots
            svg.selectAll(".dot")
                .data(sdata)
                .enter()
                .append("circle")
                .attr("class", "dot")
                .attr("cx", function(d, i){ return xScale(d.date)})
                .attr("cy", function(d, i){ return yScale(d.confirmed)})
                .attr("r", 4)
                .on("mouseover", function(d){
                    console.log(d)
                })

    });

}
