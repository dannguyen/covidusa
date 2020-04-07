---
# hey
---
;

// window.datasets = Object.is(window.datasets, undefined) ? {} : window.datasets;

const datautils = function(){
    const getSeries = function(url){
        let mypromise = d3.json(url)
                    .then(function(data){
                        let series = data.series;
                        for(let i=0; i < series.length; i++){
                            series[i].datestring = series[i].date
                            series[i].date = new Date(series[i].date)
                        }


                        return data;
                })

        return mypromise
    }

    const summaryUrl = "{{'/jdata/summary.json' | relative_url}}";



    const getSummary = function(){
        return d3.json(summaryUrl)
                    .then(function(data){
                        return data;
                    })

    }

    return {
        getSeries: getSeries,
        getSummary: getSummary,
    }

}();




    //     if(Object.is(window.datasets.timeseries, undefined)){
    //         // window.datasets.timeseries = await d3.csv(DATA_URL, function(d){
    //         //     return {id: d.id, date: new Date(d.date), confirmed: +d.confirmed, deaths: +d.deaths}
    //         // })
    //         d3.csv(DATA_URL, function(d){
    //             return {id: d.id, date: new Date(d.date), confirmed: +d.confirmed, deaths: +d.deaths}
    //         }).then(function(data){
    //             window.datasets.timeseries = data;
    //             return window.datasets.timeseries;
    //         })


    //     }else{
    //         return window.datasets.timeseries;
    //     }
    // }
