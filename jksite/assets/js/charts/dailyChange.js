---
# hi
---

;
var qy = 1, zy =1;

var DATA_URL = "{{ '/static/data/timeseries.csv?v=' | append: site.github.build_revision | relative_url }}"


function renderChangeChart(svgId, abbr){
    var svg = d3.select('#'+svgId),
        width = svg.node().getBoundingClientRect().width,
        height = svg.node().getBoundingClientRect().height;


    console.log("width: ", width, "height: ", height)



    var seriesPromise = d3.csv(DATA_URL, function(d, i){
        return {id: d.id, date: new Date(d.date), confirmed: +d.confirmed, deaths: +d.deaths}
    });


    Promise.all([seriesPromise])
        .then(function(the_response){
            zy = the_response[0]
            var sdata = qy = the_response[0].filter(function(d){ return d.id== abbr && d.confirmed > 0})
            sdata.forEach(function(d, i){
                var a = sdata[i-1]
                if(i == 0){
                    d.delta = 10;
                }else if(a.confirmed < 1){
                    d.delta = 10;
                }else{
                    d.delta = 100 * (d.confirmed - a.confirmed)/a.confirmed
                }
            })


            var xScale = d3.scaleBand()
                            .rangeRound([0, width], 0.05)
                            .padding(0.1)
                            .domain(sdata.map(function(d){ return d.date }))


            console.log("hey: ", xScale.bandwidth())
            console.log(sdata.map(function(d){ return d.date }))

            var yScale = d3.scaleLog()
                            .domain([10, d3.max(sdata, function(d){ return d.delta })])
                            .rangeRound([height, 0])

            svg.selectAll("bar")
                .data(sdata)
                .enter()
                .append("rect")
                .style("fill", "steelblue")
                .attr("x", function(d){ return xScale(d.date)})
                .attr("width", xScale.bandwidth())
                .attr("y", function(d){ return yScale(d.delta)})
                .attr("height", function(d){ return height - yScale(d.delta)})
                .on("mouseover", function(d){
                    console.log(d)
                })
            // svg.append("path")
            //     .datum(sdata)
            //     .attr("class", "line")
            //     .attr("d", dline)
            // // add dots
            // svg.selectAll(".dot")
            //     .data(sdata)
            //     .enter()
            //     .append("circle")
            //     .attr("class", "dot")
            //     .attr("cx", function(d, i){ return xScale(d.date)})
            //     .attr("cy", function(d, i){ return yScale(d.delta)})
            //     .attr("r", 4)
            //     .on("mouseover", function(d){
            //         console.log(d)
            //     })

    });

}
