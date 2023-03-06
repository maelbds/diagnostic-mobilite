import React from 'react';

import Info from '../f-Utilities/Info'
import SourcesRow from '../f-Utilities/SourcesRow'

import {formatFigure} from '../f-Utilities/util_func'

function IssuesGeneral(props){
    let territory = props.territory;
    let key_figures_total = territory.travels_analysis["1_key_figures"].total

    let total_ghg = key_figures_total.ghg_emissions == null ? "/" : formatFigure(key_figures_total.ghg_emissions * 365, 3)
    let ghg_per_hab = key_figures_total.ghg_emissions == null ? "/" : formatFigure(Math.round(key_figures_total.ghg_emissions * 365 /key_figures_total.pop*10)/10)

    return(
      <div className="row">
        <div className="col">
          <div className="row mb-0">
            <div className="col-auto">
              <h3 className="">enjeux</h3>
            </div>
          </div>
          <div className="row">
            <div className="col">
              <p><span className="key_figure red-text">{total_ghg} tCO2</span>eq/an émissions de GES (gaz à effet de serre)
              <Info content="La stratégie nationale bas-carbone française (SNBC) s’est fixée comme objectif une diminution de 28 % des émissions de la mobilité en 2030 par rapport à 2015."/></p>
              <p>→ <b>{ghg_per_hab}</b> tCO2eq/hab/an</p>
              {/*<p className="mt-3"><span className="key_figure red-text">{Math.round(territory.issues.fuel_cost_total/territory.all_travels.total_hh)} €</span> /mois budget carburant moyen par ménage</p>*/}
            </div>
          </div>


          <div className="row mt-1"></div>
          {Object.keys(props.territory.sources).includes("emd") ?
            <SourcesRow sources={props.territory.sources}
                   concerned={["emd"]}/> :
             <SourcesRow sources={props.territory.sources}
                    concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}

        </div>
      </div>

  );
}

export default IssuesGeneral;
