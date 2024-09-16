import React, { Component } from 'react';

class LegendAAV extends React.Component {
  render() {

    const typo_zaav = [{"libelle":"< 50 000 hab","couleur_pole":"#F6B7C2","couleur_couronne":"#F5F0AF"},
                       {"libelle":"50 000 - 200 000 hab","couleur_pole":"#F15D7D","couleur_couronne":"#EDE049"},
                       {"libelle":"200 000 - 700 000 hab","couleur_pole":"#E40038","couleur_couronne":"#FFB520"},
                       {"libelle":"> 700 000 hab","couleur_pole":"#A91535","couleur_couronne":"#EE9008"},
                       {"libelle":"Hors attraction des villes","couleur":"#F3F2F0"}]

    return(

  <div className="row">
    <div className="col">

      <p className="mb"><b>Typologie des communes en aire d'attraction des villes</b></p>
      <p className="mb-2"><i>(population de l'aire)</i></p>

          {[0, 1, 2, 3].map((i)=>
            <div className="row" key={"legend"+i}>
              <div className="col-auto">
                <div className="row no-gutters align-items-center">
                  <div className="col-auto mr-1">
                    <div style={{height: "15px", width: "30px", backgroundColor: typo_zaav[i].couleur_pole, border: "1px solid white", borderRadius: "3px"}}></div>
                  </div>
                  <div className="col">
                    <p>Pôle</p>
                  </div>
                </div>
              </div>
              <div className="col-auto">
                <div className="row no-gutters align-items-center">
                  <div className="col-auto mr-1">
                    <div style={{height: "15px", width: "30px", backgroundColor: typo_zaav[i].couleur_couronne, border: "1px solid white", borderRadius: "3px"}}></div>
                  </div>
                  <div className="col">
                    <p>Couronne</p>
                  </div>
                </div>
              </div>
              <div className="col">
                <p>{typo_zaav[i].libelle}</p>
              </div>
            </div>
          )}

          <div className="row no-gutters align-items-center">
            <div className="col-auto mr-1">
              <div style={{height: "15px", width: "30px", backgroundColor: typo_zaav[4].couleur, border: "1px solid white", borderRadius: "3px"}}></div>
            </div>
            <div className="col">
              <p>{typo_zaav[4].libelle}</p>
            </div>
          </div>


    </div>
  </div>
    )
  }
}

export default LegendAAV;
