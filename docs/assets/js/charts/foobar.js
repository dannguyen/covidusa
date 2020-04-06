let svg = d3.select("#mywrap").append("svg")


let sWidth = svg.node().getBoundingClientRect().width,
    sHeight = svg.node().getBoundingClientRect().height,
    margin = {top: 20, right: 15, bottom: 30, left: 25};

let width = sWidth - (margin.left + margin.right),
    height = sHeight - (margin.top + margin.bottom)


console.log(`width ${width}, height ${height}`)





const dataset = [

    [new Date("2020-03-25"), 5 ],
    [new Date("2020-03-26"), 10],
    [new Date("2020-03-27"), 34],
    [new Date("2020-03-28"), 62],
    [new Date("2020-03-29"), 26],
    [new Date("2020-03-30"), 12],
    [new Date("2020-03-31"), 0],
    [new Date("2020-04-01"), 24],
    [new Date("2020-04-02"), 56],


]

let xScale = d3.scaleTime()
                .domain(d3.extent(dataset, d => d[0]))
                .range([0, width])

let xAxis = d3.axisBottom().scale(xScale);




let yScale = d3.scaleLinear()
                .domain([0, 100])
                .rangeRound([height, 0])


// yScale
//     .map(yScale.tickFormat(10, ""))


let yAxis = d3.axisRight()
                .scale(yScale)



/// render

svg.selectAll("rect")
    .data(dataset)
    .enter()
    .append('rect')
    .attr("x", (d, i) => xScale(d[0]))
    .attr("width", (d, i) => 15)
    .attr("y", (d, i) => yScale(d[1]))
    .attr("height", (d, i) => height - yScale(d[1]))
    .attr("stroke", "black")



svg.append("g")
        .call(xAxis)
        .attr("transform", `translate(0,${height})`)


svg.append("g")
    .call(yAxis)
    .attr("transform", `translate(${width},0)`)

