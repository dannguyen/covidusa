var svg = d3.select("#mapbox"),
    width = +svg.attr("width"),
    height = +svg.attr("height");


// var url = "https://d3js.org/us-10m.v1.json"

var states_url = "/covidusa/static/data/topo/states.topo.json?v=0.0.1a"


var us_states = d3.json(states_url);
var xstates = 1;
Promise.all([us_states])
.then(function(the_response){
    console.log("fetched url", the_response)
    geodata = the_response[0]

//    var projection = d3.geoAlbers().scale(800) //.fitWidth(width, glob) //.fitWidth(width, gdata) // .fitSize([width, height]);
    var path = d3.geoPath()

    var states = topojson.feature(geodata, geodata.objects.states).features
    xstates = states


    svg.selectAll("path")
        .data(states)
        .enter()
        .append("path")
        .attr("class", "state")
        .attr("d", path)
        .attr("")


    // svg.append("g")
    //     .attr("class", "states")
    //     .selectAll("path")
    //     .data(states)
    //     .enter()
    //     .append("path")
    //     .attr("d", path)

    // svg.selectAll("text")
    //     .data(states)
    //     .enter()
    //     .append("text")
    //     .text(function(d){
    //         return "hi"
    //     })
    //     // .attr("x", function(d) {return projection([d.Longitude, d.Lattitude])[0] + 5;})
    //     // .attr("y", function(d) {return projection([d.Longitude, d.Lattitude])[1] + 15;})
    //     .attr("class", "abbr")


})
.catch(function(error){
    if (error) throw error;

})
