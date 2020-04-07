const dailyCounts = function(){
    const renderConfirmed = function(id, target_id){


        let pfoo = datautils.getEntity(id);
        Promise.resolve(pfoo)
            .then(function(resp){
                let data = resp;
                let records = data.records;


        let svg = d3.select('#'+target_id),
            width = svg.node().getBoundingClientRect().width,
            height = svg.node().getBoundingClientRect().height,
            margin = {top: 20, right: 35, bottom: 20, left: 10}



                let xScale = d3.scaleTime()
                                .domain(d3.extent(records, d => d.date ))
                                .range([0, width - margin.right]);

                let xAxis = d3.axisBottom()
                                .scale(xScale);

                svg.append("g")
                    .attr("transform", `translate(0,${height - margin.bottom})`)
                    .call(xAxis);


                let yScale = d3.scaleLog()
                                .domain([1, d3.max(records, function(d){ return d.confirmed })])
                                .range([height-margin.bottom, 0])


                let yAxis = d3.axisRight()
                                .scale(yScale);

                svg.append("g")
                    .attr("transform", `translate(${width - margin.right},0)`)
                    .call(yAxis);



                let dline = d3.line()
                    .x(function(d){ return xScale(d.date)})
                    .y(function(d){ return yScale(d.confirmed)})
                    .curve(d3.curveMonotoneX);


                // (g, x) => g
                //     .attr("transform", `translate(0,${height - margin.bottom})`)
                //     .call(d3.axisBottom(x).ticks(width / 80, "%"))
                //     .call(g => (g.selection ? g.selection() : g).select(".domain").remove())



                svg.append("path")
                    .datum(records)
                    .attr("class", "line")
                    .attr("d", dline)
                // add dots
                svg.selectAll(".dot")
                    .data(records)
                    .enter()
                    .append("circle")
                    .attr("class", "dot")
                    .attr("cx", function(d, i){ return xScale(d.date)})
                    .attr("cy", function(d, i){ return yScale(d.confirmed)})
                    .attr("r", 4)
                    .on("mouseover", function(d){
                        console.log(d)
                    });

            })
    };


    return {
        renderConfirmed: renderConfirmed
    }

}();


