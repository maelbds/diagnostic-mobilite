import React, { Component } from 'react';
import LeafletMapCaseStudy from '../b-LeafletMap/LeafletMapCaseStudy';
import PlotPie from '../c-PlotlyFigures/PlotPie'


class CaseStudy extends React.Component {

  render() {
    var territory = this.props.territory;

    return(
      <div className="row">
        <div className="col">

          <div className="row mt-5 mb-2">
            <div className="col-12">
              <h2 className="line">étude de cas</h2>
            </div>
          </div>


            <div className="row mt-5 mb-4">
              <div className="col-12">
                {<LeafletMapCaseStudy territory={territory}
                                         id="case_study_work"/>}
              </div>
            </div>

        </div>
      </div>
    )
  }
}

export default CaseStudy;
