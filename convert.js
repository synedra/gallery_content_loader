const csv=require('csvtojson')

const converter=csv({
    trim:true,
})

csv().fromFile('sampleapps.csv')
.subscribe((json)=>{
    return new Promise((resolve,reject)=>{
        console.log(json)
        // Async operation on the json
        // don't forget to call resolve and reject
    })
})