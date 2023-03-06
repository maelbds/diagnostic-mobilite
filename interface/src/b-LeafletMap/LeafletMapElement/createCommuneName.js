const L = window.L;

export function createCommunesNamesLayerEasy(communes){
  let epci = [...new Set(communes.map((c)=>c.epci_code))]
  let communes_for_names = [];
  if (epci.length <= 5){
    communes_for_names = communes.slice().sort((c1, c2)=> c2.population - c1.population).slice(0, 10)
  }
  else{
    let dict_epci={}
    for (let e of epci){
      dict_epci[e] = communes.filter((c)=>c.epci_code == e).sort((c1, c2) => c2.population - c1.population)[0]
    }
    communes_for_names = Object.values(dict_epci)
  }

  let coords = communes_for_names.map((c)=>c.center)
  let names = communes_for_names.map((c)=>c.name)

  var nameMarkers = [];
  for (var i=0; i<coords.length; i++){
      let nameIcon = L.divIcon({
        className: 'my-div-icon',
        html: '<p class="map name">' + names[i] + "</p>"
      });
      let nameMarker = L.marker(coords[i], {icon: nameIcon});
      nameMarkers.push(nameMarker);
  }
  let names_layer = L.featureGroup(nameMarkers);
  return names_layer
}
