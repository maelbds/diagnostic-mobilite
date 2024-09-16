import React, { Component } from 'react';

class DownloadButtonLight extends React.Component {

  render() {
    return(
      <div className="col-auto pl-0">
        <p className="button-download p-0 pl-2 pr-2"
           title={this.props.title}
           onClick={this.props.onClick}
           >
          <span className={"material-symbols-outlined download"}>download</span> {this.props.label}
        </p>
      </div>
    )
  }
}

export default DownloadButtonLight;
