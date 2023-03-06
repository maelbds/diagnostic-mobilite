import React, { Component } from 'react';

import SourcesRow from '../f-Utilities/SourcesRow';
import Legend from './Legend/Legend';

class LeafletMapLegend extends React.Component {

  render() {
    return(
      <div className="row">
        <div className="col">
          <div className="row align-items-end">

            <div className="col-10">
              <div style={{height: this.props.height}} id={this.props.id}></div>
            </div>
            <div className="col-2 pl-0 pr-0">
                <Legend legend={this.props.legend} />
            </div>

          </div>

          <div className="row">
            <div className="col-10">
              <SourcesRow sources={this.props.all_sources} concerned={this.props.concerned_sources}/>
            </div>
          </div>

        </div>
      </div>
    )
  }
}

export default LeafletMapLegend;
