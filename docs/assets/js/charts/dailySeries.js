const dailySeries = function(){
    const renderConfirmed = function(id, target_id, url){
        let svg = d3.select('#'+target_id),
            width = svg.node().getBoundingClientRect().width,
            height = svg.node().getBoundingClientRect().height;


        let pfoo = datautils.getSeries(url);
        Promise.resolve(pfoo)
            .then(function(resp){
                let data = resp;
//                console.log(data)
                let series = data['series'].sort((x, y) => x.date - y.date )

                var xScale = d3.scaleTime()
                                .domain(d3.extent(series, function(d){ return d.date }))
                                .range([0, width])

                var yScale = d3.scaleLog()
                                .domain([1, d3.max(series, function(d){ return d.confirmed })])
                                .range([height, 0])

                var dline = d3.line()
                    .x(function(d){ return xScale(d.date)})
                    .y(function(d){ return yScale(d.confirmed)})
                    .curve(d3.curveMonotoneX);


                svg.append("path")
                    .datum(series)
                    .attr("class", "line")
                    .attr("d", dline)
                // add dots
                svg.selectAll(".dot")
                    .data(series)
                    .enter()
                    .append("circle")
                    .attr("class", "dot")
                    .attr("cx", function(d, i){ return xScale(d.date)})
                    .attr("cy", function(d, i){ return yScale(d.confirmed)})
                    .attr("r", 4)
                    .on("mouseover", function(d){
                        console.log(d)
                    })

            })
    };


    return {
        renderConfirmed: renderConfirmed
    }

}();


