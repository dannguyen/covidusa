;

// window.datasets = Object.is(window.datasets, undefined) ? {} : window.datasets;

const datautils = function(){
    const entitiesDir = "/covidusa/jdata/entities";
    const getEntity = function(eid){
        let url = `${entitiesDir}/${eid}.json`;
        console.log('getEntity url:', url)
        let mypromise = d3.json(url)
                    .then(function(data){
                        let records = data.records;
                        for(let i=0; i < records.length; i++){
                            records[i].datestring = records[i].date
                            records[i].date = new Date(records[i].date)
                        }


                        return data;
                })

        return mypromise
    }

    const summaryUrl = "/covidusa/jdata/summary.json";



    const getSummary = function(){
        return d3.json(summaryUrl)
                    .then(function(data){
                        return data;
                    })

    }

    return {
        getEntity: getEntity,
        getSummary: getSummary,
    }

}();
