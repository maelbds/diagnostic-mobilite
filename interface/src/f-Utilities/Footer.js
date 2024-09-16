import React, { Component } from 'react';

import {c_light, c_dark} from '../a-Graphic/Colors';

class Header extends React.Component{
  constructor(props) {
   super(props);
  }

  componentDidMount(){
    var part1 = "mael";
    var part2 = Math.pow(2,6);
    var part3 = String.fromCharCode(part2);
    var part4 = "mobam.fr";
    var part5 = part1 + String.fromCharCode(part2) + part4;

    var courrier = document.getElementById("courrier");
    courrier.innerHTML = "<a href=" + "mai" + "lto" + ":" + part5 + ">" + part5 + "</a>";
  }

  render(){
    return(
      <div className="row mt-5" id="footer">
        <div className="col">

            <div className="row justify-content-center pt-4 pb-5" style={{backgroundColor: c_dark}}>
              <div className="col-11">

                <div className="row justify-content-between">
                  <div className="col-md-6 col-12 description">

                    <div className="row">
                      <div className="col-12">
                        <p className="mb-1">Diagnostic Mobilité s'adresse à tous les acteurs de la mobilité durable : les territoires (AOM ou non) et institutions,
                        les bureaux d'études et opérateurs de solutions de (dé)mobilité, les initiatives citoyennes et associations.
                        Il s'organise sous la forme d'un commun et les contributions sont les bienvenues. <a href="https://diagnostic-mobilite.fr/" target="_blank">En savoir plus</a></p>
                      </div>
                    </div>

                    <div className="row mt-3 mb-5 align-items-center">
                      <div className="col-9">
                        <p className="mb-1">Ce projet a été initié par Jean Coldefy, directeur du programme Mobilités et transitions au
                        sein de l’association <a href="https://atec-its-france.com/" target="_blank">ATEC ITS France</a> et Maël Bordas, consultant indépendant, dans le cadre de l'appel à communs <a href="https://wiki.resilience-territoire.ademe.fr/wiki/Diagnostic_Mobilit%C3%A9" target="_blank">Résilience des territoires</a> de l'ADEME.</p>
                      </div>
                      <div className="col-3">
                        <img src="images/ademe_v.jpg" className="img-fluid" style={{borderRadius: "4px"}}/>
                      </div>
                    </div>

                  </div>

                  <div className="col-md-4 col-12">
                    <h4 className="mb-2">ressources</h4>
                    <p className="mb-1"><a href="https://diagnostic-mobilite.fr/docs/guide_methodologique_Diagnostic_Mobilite.pdf" target="_blank">Guide méthodologique</a></p>
                    <p className="mb-1"><a href="https://github.com/maelbds/diagnostic-mobilite" target="_blank">Répertoire GitHub de l'outil</a></p>
                    <p className="mb-1"><a href="https://diagnostic-mobilite.fr/docs/extrait_cadre_de_ville.mp4" target="_blank">Vidéo de démonstration de l'outil  (webinaire Cadre de Ville)</a></p>

                    <h4 className="mb-2 mt-4">contact</h4>
                    <p className="mb-4"><span id="courrier"></span></p>
                  </div>
                </div>
              </div>
            </div>

        </div>
      </div>
    );
  }
}

export default Header;
