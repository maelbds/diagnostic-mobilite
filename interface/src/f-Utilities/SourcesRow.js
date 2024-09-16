import React, { Component } from 'react';

import SourcesP from './SourcesP';

class SourcesRow extends React.Component {

  render() {
    return(
      <div className="row mt-1">
        <div className="col">
         <SourcesP selected_sources={this.props.selected_sources}/>
        </div>
      </div>
    )
  }
}

export default SourcesRow;
