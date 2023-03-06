import React, { Component } from 'react';

import SourcesP from './SourcesP';

class SourcesRow extends React.Component {

  render() {
    return(
      <div className="row mt-1">
        <div className="col">
         <SourcesP sources={this.props.sources}
                   concerned={this.props.concerned}/>
        </div>
      </div>
    )
  }
}

export default SourcesRow;
