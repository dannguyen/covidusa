;

const dailyChange = function(){

    const renderConfirmed = function(id, target_id, url){

        let pfoo = datautils.getSeries(url);
        Promise.resolve(pfoo)
            .then(function(resp){
                let data = resp;
                let series = data['series']; //.sort((x, y) => x.date - y.date )


                let svg = d3.select('#'+target_id),
                    width = svg.node().getBoundingClientRect().width,
                    height = svg.node().getBoundingClientRect().height,
                    margin = {top: 20, right: 35, bottom: 20, left: 10};



                let xScale = d3.scaleBand()
                                .rangeRound([0, width], 0.05)
                                .padding(0.1)
                                .domain(series.map(function(d){ return d.date }))


                let xAxis = d3.axisBottom()
                                .scale(xScale);


                svg.append("g")
                    .attr("transform", `translate(0,${height - margin.bottom})`)
                    .call(xAxis);


                let yScale = d3.scaleLog()
                                .domain([1, d3.max(series, function(d){ return d.confirmed_daily_diff_pct })])
                                .rangeRound([height-margin.bottom, 0])


                let yAxis = d3.axisRight()
                                .scale(yScale);

                svg.append("g")
                    .attr("transform", `translate(${width - margin.right},0)`)
                    .call(yAxis);



                svg.selectAll("bar")
                    .data(series)
                    .enter()
                    .append("rect")
                    .style("fill", "steelblue")
                    .attr("x", function(d){ return xScale(d.date)})
                    .attr("width", xScale.bandwidth())
                    .attr("y", function(d){
                        let pct = d.confirmed_daily_diff_pct;
                        if(pct > 0){
                            return yScale(pct);
                        }else{
                            return 0
                        }
                    })
                    .attr("height", function(d){
                        let pct = d.confirmed_daily_diff_pct;
                        if(pct > 0){
                            return height - yScale(pct);
                        }else{
                            return 0
                        }
                    })
                    .on("mouseover", function(d){
                        console.log(`${d.date}: diff: ${d.confirmed_daily_diff} pct: ${d.confirmed_daily_diff_pct}%`)
                    })

            });


    };

    return {
        renderConfirmed: renderConfirmed
    }


}();

