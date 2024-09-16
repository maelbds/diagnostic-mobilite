import React, { Component } from 'react';

class SelectionMapInfo extends React.Component {

  render() {
    if (this.props.info.geo_code == null){
      return (
        <div className="col" id="info">
          <p>Survoler la carte pour afficher les informations de la commune. Cliquer pour ajouter au territoire d'étude.</p>
        </div>
      )
    } else {
      let {geo_code, name_commune, name_epci, name_arr, name_dep, name_aav, name_typo_aav} = this.props.info

      let aav
      if(name_typo_aav == "") aav = name_aav
      else aav = name_typo_aav + " - " + name_aav

      return (
        <div className="col" id="info">
          <p className="mb-2"><b>{name_commune}</b> ({geo_code})</p>

          <p><span style={{borderBottom: "1px solid grey"}} className="mr-2">EPCI</span> {name_epci}</p>
          <p><span style={{borderBottom: "1px solid grey"}} className="mr-2">Arrondissement</span> {name_arr}</p>
          <p><span style={{borderBottom: "1px solid grey"}} className="mr-2">Département</span> {name_dep}</p>

          <p className="mt-2">{aav}</p>
        </div>
      )
    }



  }
}

export default SelectionMapInfo;
