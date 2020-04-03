// DTK
// const dailyTable = function(){
//     const headermap = {
//         'datestring': 'Date',
//         'confirmed': 'Confirmed',
//         'confirmed_diff_pct': 'Confirmed % Change',
//         'deaths': 'Deaths'
//     }

//     const headers = Object.keys(headermap);

//     function render(id, target_id, url){
//         console.log('table about to render', id)
//         Promise.resolve(datautils.getSeries(url))
//             .then(function(resp){
//                 let data = resp;
//                 let series = resp['series']
//                 let target = d3.select("#"+target_id);

//                 target.append("thead")
//                     .append("tr")
//                     .selectAll('th')
//                     .data(headers.map(h => headermap[h]))
//                     .enter()
//                     .append('th')
//                     .text(d => d);

//                 let rows = target.selectAll('tr')
//                     .data(series)
//                     .enter()
//                     .append('tr')

//                 rows.selectAll('td')
//                     .data(d => headers.map(h => [h, d[h]]) )
//                     .enter()
//                     .append('td')
//                     .attr("class", d => d[0])
//                     .text(d => d[1])
//         })

//     }



//     return {
//         render: render
//     }

// }()

