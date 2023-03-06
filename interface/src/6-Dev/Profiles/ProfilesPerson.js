import React, { Component } from 'react';


class ProfilesPerson extends React.Component {

  render() {
    var age = this.props.person.age
    var cars_nb = this.props.person.cars_nb
    var residential_area = this.props.person.residential_area
    var hh_nb = this.props.person.households_nb
    var hh_nb_child = this.props.person.households_nb_child

    return(
      <div className="row mb-3">
        <div className="col">
          <p>{age} ans</p>
          <p>habite à {residential_area}</p>
          <p>{hh_nb} personne(s) dans le ménage</p>
          <p>dont {hh_nb_child} enfant(s)</p>
          <p>{cars_nb} voiture(s)</p>
        </div>
      </div>

    )
  }
}

export default ProfilesPerson;
