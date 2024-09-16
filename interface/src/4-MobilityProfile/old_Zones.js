import React from 'react';
import {c_zones} from '../a-Graphic/Colors';

import getMyMap from '../b-LeafletMap/leaflet_map';
import {createCommunesLayer} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';

import {formatFigure} from '../f-Utilities/util_func'

import ZonesItemExchange from './ZonesItemExchange'
import ZonesItem from './ZonesItem'
import PlotPie from '../c-PlotlyFigures/PlotPie'
import LegendModes from '../f-Utilities/Legend/LegendModes'

import SourcesRow from '../f-Utilities/SourcesRow'

const L = window.L;


class Zones extends React.Component {
   constructor(props) {
    super(props);

    this.state = {
      unit: "distance",
      label: "km"
    };
  }

  setUnit = (unit, label) => {
      this.setState({
        unit: unit,
        label: label
      })
  }

  componentDidMount() {
    /* COMMUNES */
    let communes = this.props.territory.communes;

    let zm = this.props.territory.travels_analysis["2_zones"].zones_modes;
    let zones = Object.keys(zm).map((z) => parseFloat(z)).filter((zm) => zm>0);

    let main_zones = zones.slice(0, -1)
    let communes_coords_mz = communes.filter((c)=>main_zones.includes(c.zone)).map((c) => c.center);
    let communes_names_mz = communes.filter((c)=>main_zones.includes(c.zone)).map((c) => c.name);


    // --- init map
    let mymap = getMyMap(this.props.id, true, 0.1);

    // --- create layers
    let zones_layers = []
    zones.map((z)=>
      zones_layers.push(createCommunesLayer(communes.filter((c)=>c.zone==z),
                                            communes.filter((c)=>c.zone==z).map((c) => c.name + " - Zone " + z),
                                            c_zones[z]))
    )
    let zones_layers_group = L.featureGroup(zones_layers);
    zones_layers_group.addTo(mymap);

    let layer_names = createCommunesNamesLayerEasy(communes);
    layer_names.addTo(mymap);

    // --- center the map
    mymap.fitBounds(zones_layers_group.getBounds());
  }

    render(){
      function label_text(status){
        var total = Object.values(status).reduce((a,b) => a + b);
        var text = Object.fromEntries(
                    Object.entries(status).map(
                      ([k, v], i) => [k, "<span style='font-size: 15px;'>" + Math.round(v/total*1000)/10 +
                                        " %</span></br></br><span style='font-weight: 300; font-size: 15px'>" + k + "</span>" ]
                    )
                  );
        return(Object.values(text))
      }

      function hover_text(status){
        var text = Object.fromEntries(
                    Object.entries(status).map(
                      ([k, v], i) => [k, k + "</br></br><span style='font-weight: 300;'>" + Math.round(v) + " déplacements</span>"]
                    )
                  );
        return(Object.values(text))
      }
      function filter_domicile(data){
        return Object.assign({}, ...Object.entries(data).filter(([k,v]) => k != "domicile").map(([k,v]) => ({[k]:v})));
      }

      let territory = this.props.territory;
      let zm = territory.travels_analysis["2_zones"].zones_modes;
      let zmg = territory.travels_analysis["2_zones"].zones_modes_global;
      let zones = Object.keys(zm);
      let zones_nb = Math.max(...zones.map((z)=>parseFloat(z)));

      let prop_travels_with_no_zone = Math.round(territory.travels_analysis["2_zones"].zones_missing[this.state.unit]/territory.travels_analysis["1_key_figures"].total[this.state.unit]*1000)/10
      let z =3

      // figures for lecture notice
      let zone_1_1_walk = zm[1][1][this.state.unit]["à pied"]
      let zone_1_1_all = zmg[this.state.unit]["zones_1_1"]
      let all_travels = territory.travels_analysis["1_key_figures"].total[this.state.unit]

      let zone_0_1_car = zm[-1][1][this.state.unit]["voiture"]
      let zone_0_1_all = zmg[this.state.unit]["zones_-1_1"]

      return(
        <div className="row mt-5">
          <div className="col">

          <div className="row">
            <div className="col-auto">
              <h3 className="mb-3">modes de déplacements au sein et entre zones</h3>
            </div>
          </div>

          <div className="row">
            <div className="col-7">
              <div style={{height: "450px"}} id="zones"></div>
            </div>
            <div className="col-5">
              <p className="mb-1">Dans cette section, on analyse les parts modales des déplacements effectués au sein d'une zone ou entre des zones. On étudie également la répartition générale des déplacements entre les zones.
              Comme dans les autres sections, les déplacements sont comptés en <i>nombre</i>, en <i>distance parcourue</i> ou en <i>émissions de GES</i>, suivant le bouton sélectionné ci-dessous.</p>
              <p className="mb-1">Par exemple, parmi tous les déplacements effectués <span style={{backgroundColor: c_zones[1]+"bf"}}>au sein de la zone 1</span>, on compte <b>{Math.round(zone_1_1_walk/zone_1_1_all*100)}% des {this.state.label}</b> qui sont <b>faits à pied.</b> Les déplacements
                  effectués <span style={{backgroundColor: c_zones[1]+"bf"}}>au sein de la zone 1</span> représentent eux-mêmes <b>{Math.round(zone_1_1_all/all_travels*100)}% des {this.state.label} de l'ensemble des
                  déplacements réalisés par la population du territoire</b>, soit {formatFigure(zone_1_1_all, 3)} {this.state.label}.</p>
              <p className="mb-3">On peut aussi lire que, parmi les déplacements effectués entre la <span style={{backgroundColor: c_zones[1]+"bf"}}>zone 1</span> et l'<span style={{backgroundColor: c_zones[0]+"bf"}}>extérieur</span>,
              on compte <b>{Math.round(zone_0_1_car/zone_0_1_all*100)}% de {this.state.label}</b> qui sont <b>faits en voiture.</b> Les déplacements entre la <span style={{backgroundColor: c_zones[1]+"bf"}}>zone 1</span> et l'<span style={{backgroundColor: c_zones[0]+"bf"}}>extérieur</span> répresentant
              eux-mêmes <b>{Math.round(zone_0_1_all/all_travels*100)}% des {this.state.label} de l'ensemble des
              déplacements</b>, soit {formatFigure(zone_0_1_all, 3)} {this.state.label}.</p>
              <p>Enfin, on note que la précision statistique n'est pas toujours suffisante pour détailler tous les résultats, d'où la mention <i>autre/imprécis</i>.</p>
            </div>
          </div>

          <div className="row mt-4 mb-4">
          <div className="col-2">
            <p onClick={this.setUnit.bind(this, "distance", "km")}
               className={this.state.unit == "distance" ? "button p-1 active" : "button p-1"}>Distance parcourue</p>
          </div>
            <div className="col-2 pl-0">
              <p onClick={this.setUnit.bind(this, "number", "déplacements")}
                 className={this.state.unit == "number" ? "button p-1 active" : "button p-1"}>Nombre de déplacements</p>
            </div>
            <div className="col-2 pl-0">
              <p onClick={this.setUnit.bind(this, "ghg_emissions", "tCO2eq")}
                 className={this.state.unit == "ghg_emissions" ? "button p-1 active" : "button p-1"}>Emissions de GES</p>
            </div>
          </div>

          <LegendModes/>

            <div className="row mt-3">
            {[...Array(zones_nb + 1).keys()].slice(1,).map((z)=>
              <div className={"col-" + 12/(zones_nb+1)}>
                <ZonesItem territory={territory} unit={this.state.unit} main_zone={z} zones_nb={zones_nb} significance_threshold={this.props.significance_threshold} label={this.state.label} />
              </div>
            )}
              <div className={"col-" + 12/(zones_nb+1)}>
                <ZonesItem territory={territory} unit={this.state.unit} main_zone={-1} zones_nb={zones_nb} significance_threshold={this.props.significance_threshold} label={this.state.label} />
              </div>
            </div>

            {zones_nb == 3 &&
            <div className="row">
              <div className="col-9">
                <div className="row">
                  <div className="col">
                    <ZonesItemExchange territory={territory} unit={this.state.unit} zone_from={1} zone_to={2} significance_threshold={this.props.significance_threshold} label={this.state.label}/>
                  </div>
                  <div className="col">
                    <ZonesItemExchange territory={territory} unit={this.state.unit} zone_from={2} zone_to={3} significance_threshold={this.props.significance_threshold} label={this.state.label}/>
                  </div>
                </div>
              </div>
            </div>}

          {zones_nb == 3 &&
            <div className="row">
              <div className="col-9">
                <div className="row">
                  <div className="col">
                    <ZonesItemExchange territory={territory} unit={this.state.unit} zone_from={1} zone_to={3} significance_threshold={this.props.significance_threshold} label={this.state.label}/>
                  </div>
                </div>
              </div>
            </div>}

            {zones_nb == 2 &&
            <div className="row">
              <div className="col-8">
                <div className="row">
                  <div className="col">
                    <ZonesItemExchange territory={territory} unit={this.state.unit} zone_from={1} zone_to={2} significance_threshold={this.props.significance_threshold} label={this.state.label}/>
                  </div>
                </div>
              </div>
            </div>}

            {[...Array(zones_nb + 1).keys()].slice(1,).reverse().map((z)=>
              <div className="row">
                <div className={"col offset-" + (12/(zones_nb+1)*(z-1))}>
                  <ZonesItemExchange territory={territory} unit={this.state.unit} zone_from={z} zone_to={-1} significance_threshold={this.props.significance_threshold} label={this.state.label}/>
                </div>
              </div>
            )}


            <div className="row mt-1 mb-4">
              <div className="col-12">
                <p>L'origine ou la destination de certains déplacements n'ont pas pu être identifiées, ils représentent {prop_travels_with_no_zone}% des déplacements.</p>
              </div>
            </div>

            {Object.keys(this.props.territory.sources).includes("emd") ?
            <SourcesRow sources={this.props.territory.sources}
                   concerned={["emd"]}/> :
             <SourcesRow sources={this.props.territory.sources}
                    concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}


          </div>
        </div>

    );
  }
}

export default Zones;
