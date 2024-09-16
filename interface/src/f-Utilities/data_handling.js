

export function lists_to_objects(lists){
  if(lists.constructor === Object){
    let objs = []
    let keys = Object.keys(lists)
    let nb_obj = lists[keys[0]].length
    for (let i=0; i<nb_obj; i++){
      let new_obj = {}
      for (let key of keys){
        new_obj[key] = lists[key][i]
      }
      objs.push(new_obj)
    }
    return objs
  } else {
    return lists
  }
}


export function enrichGeojson(geojson, features_properties){
  let properties_by_code = new Map(features_properties.map((f) => [f.geo_code, f]))
  let new_geojson = {
    type: geojson.type,
    features: geojson.features.map((f) => ({
                type: f.type,
                geometry: f.geometry,
                properties: ({...f.properties, ...properties_by_code.get(f.properties.codgeo)}),
              }))
  }
  return new_geojson
}


export function drop_duplicates_sources(sources){
  return sources.filter((s, i) => sources.map((d) => d.label).indexOf(s.label) === i)
}
