---
# hi
---
;

var qz = 9;




const dailyChange = function(){

    const renderConfirmed = function(id, target_id){

        let pfoo = datautils.getEntity(id);
        Promise.resolve(pfoo)
            .then(function(resp){
                let data = resp;
                // we truncate records to the first day of >= 100 cases
                let records = data['records'];
                // todo: pull date of confirmed_100 from summary
                records = records.slice(records.findIndex(d => d.confirmed >= 100))


                let svg = d3.select('#'+target_id),
                    sWidth = svg.node().getBoundingClientRect().width,
                    sHeight = svg.node().getBoundingClientRect().height,
                    margin = {top: 20, right: 35, bottom: 20, left: 10};


                let width = sWidth - (margin.left + margin.right),
                    height = sHeight - (margin.top + margin.bottom)

                let xScale = qz = d3.scaleUtc()
                                .domain(d3.extent(records, d => d.date))
                                .rangeRound([0, width])

                                // .padding(0.1)


                let xAxis = d3.axisBottom()
                                .scale(xScale)
                                .ticks(d3.utcWeek.every(1))


                let yMin = Math.min(0, d3.min(records, d=>d.confirmed_daily_diff_pct)),
                    yMax = Math.max(100, d3.max(records, d => d.confirmed_daily_diff_pct));
                // let yMaxLog = Math.ceil(Math.log10(yMax));
                // let yMaxAx = Math.pow(10, yMaxLog)
                // console.log(yMax, yMaxAx)
                // let yTicks = yMaxLog + 1;


                let yScale = d3.scaleLinear()
                                .domain([yMin, yMax])
                                .rangeRound([height, 0])


                let yAxis = d3.axisRight()
                                .scale(yScale)
                                // .ticks(yTicks)
                                // .tickFormat((y, i) => Math.pow(10, i))



                svg.selectAll("bar")
                    .data(records)
                    .enter()
                    .append("rect")
                    .style("fill", "steelblue")
                    .attr("x", function(d){ return xScale(d.date)})
                    .attr("width", Math.floor(width / records.length))
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

                svg.append("g")
                    .attr("class", "axis x-axis")
                    .attr("transform", `translate(0,${height})`)
                    .call(xAxis)

                let xTicks =   svg.selectAll(".x-axis g.tick text");
                console.log("xticks: ", xTicks.size())

                xTicks.attr("transform", function(d, i){
                        if(i == 0){
                            let tw = this.getBoundingClientRect().width;
                            // console.log("x-axis transform:", i, tw)
                            return `translate(${Math.round(tw / 2)}, 0)`
                        }else if(i == xTicks.size()-1){
                            let tw = this.getBoundingClientRect().width;
                            return `translate(${0-Math.round(tw / 2)},0)`
                        }
                    })

                /// format yticks
                svg.append("g")
                    .attr("class", "axis y-axis")
                    .attr("transform", `translate(${width},0)`)
                    .call(yAxis);

                let yTicks =   svg.selectAll(".y-axis g.tick text");
                yTicks.attr("transform", function(d, i){
                        let t = this.getBoundingClientRect().height;
                        // console.log("x-axis transform:", i, tw)
                        return `translate(0,${Math.round(t / 3)})`

                    })

            });


    };

    return {
        renderConfirmed: renderConfirmed
    }


}();

