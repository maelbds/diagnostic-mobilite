import React, { Component } from 'react';


class Disclaimer extends React.Component {

  render() {
    return(
      <div className="row mb-4">
        <div className="col disclaimer p-2">
          <h4 className="mb-1">à noter</h4>
          <p className="mb-1">Les données relatives aux pratiques de déplacement sont issues d’une modélisation car aucune enquête mobilité locale n'est disponible sur ce territoire.
          La modélisation estime les déplacements du territoire à partir du profil de la population locale et des comportements nationaux issus de l'EMP.</p>
          <p className="mb-1"><a href="https://diagnostic-mobilite.fr/docs/methodologie_modelisation_v1.pdf"
                target="_blank"><b>La méthodologie de modélisation et ses limites sont disponibles ici.</b></a></p>
          <p>Bien qu’elle se veuille représentative au mieux de la réalité, cette modélisation a des limites dont il faut tenir compte lors de l'interprétation.
          Ainsi, ces données permettent simplement de dégager des ordres de grandeur et d’interroger certains enjeux.
          Pour aller plus loin, une enquête locale est nécessaire (<a href="https://www.cerema.fr/fr/activites/services/realiser-enquete-mobilite-certifiee-cerema-emc2-votre"
                                                                      target="_blank">voir auprès du CEREMA</a>).</p>
        </div>
      </div>
    )
  }
}

export default Disclaimer;
