import React, { Component } from 'react';

import ProfilesTravel from './ProfilesTravel';
import ProfilesPerson from './ProfilesPerson';

class Profiles extends React.Component {

  render() {
    var profiles = this.props.territory.profiles

    var profiles_names = {
      "à la retraite": profiles.retired,
      "au chômage": profiles.unemployed,
      "avec emploi et enfant(s)": profiles.employed_with_child,
      "avec emploi et sans enfants": profiles.employed_without_child,
      "jeune (collège/lycée)": profiles.young
    }

    function handleTime(parsed_time){
      var time = parsed_time.split(":")
      return time[0] + "h" + time[1]
    }

    return(
      <div className="row">
        <div className="col-12">
          {Object.keys(profiles_names).map((name) =>
            <div className="row mt-5 mb-5 justify-content-between">
               <div className="col-12"><h3 className="line mb-4 mt-3">{name}</h3></div>
               {profiles_names[name].map((person, i) =>
                 i<4 &&
                 <div className="col-3">
                   <h4 className="mb-3">profil {i+1}</h4>
                   <ProfilesPerson person={person}/>
                   {person.travels.map((t, i) =>
                     <ProfilesTravel travel={t} last={i==person.travels.length-1}/> )}
                 </div>
               )}
             </div>
          )}

        </div>
      </div>
    )
  }
}

export default Profiles;
