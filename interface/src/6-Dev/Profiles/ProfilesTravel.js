import React, { Component } from 'react';


class ProfilesTravel extends React.Component {

  render() {
    var travel = this.props.travel

    function handleTime(parsed_time){
      var time = parsed_time.split(":")
      return time[0] + "h" + time[1]
    }

    return(
      <div className="row no-gutters">
        <div className="col-3">
          <p className="text-left"><b>{travel.dep_reason}</b></p>
        </div>
        <div className="col-10 offset-2">
          <p><i>{handleTime(travel.dep_time)}</i></p>

         <div className=" pt-2 pb-2 border border-bottom-0 border-right-0 border-top-0 border-dark">
           <p className="pl-2">{travel.mean} - {travel.distance} km</p>
         </div>

          <p><i>{handleTime(travel.des_time)}</i></p>
        </div>

          {this.props.last &&
            <div className="col-3">
              <p className="text-left"><b>{travel.des_reason}</b></p>
            </div>
          }


                {/* VERSION HORIZONTALE
                  <div className="row mb-2 mt-2 align-items-center">
                    <div className="col-12">
                      <p><i>{travel.dep_reason}</i></p>
                    </div>

                    <div className="col-10 offset-1">
                         <div className="row align-items-center">
                              <div className="col-auto pr-0">
                                <p>{handleTime(travel.dep_time)}</p>
                              </div>
                             <div className="col pl-2 pr-2">
                               <p className="border border-right-0 border-left-0 border-top-0 border-dark text-center">{travel.mean}</p>
                               <p className="text-center">{travel.distance} km</p>
                             </div>
                              <div className="col-auto pl-0">
                                <p className="text-right">{handleTime(travel.des_time)}</p>
                              </div>
                          </div>
                    </div>

                    {this.props.last &&
                      <div className="col-12">
                        <p><i>{travel.des_reason}</i></p>
                      </div>
                    }
                  </div>*/}
      </div>

    )
  }
}

export default ProfilesTravel;
