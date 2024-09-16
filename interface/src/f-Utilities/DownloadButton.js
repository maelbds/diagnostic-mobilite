import React, { Component } from 'react';

class DownloadButton extends React.Component {

  render() {
    return(
      <div className="col-auto pl-2 pr-1">
        <p onClick={this.props.download}
           className="p-1 button_csv">{this.props.label}</p>
      </div>
    )
  }
}

DownloadButton.defaultProps = {
  label: "Télécharger le tableau au format CSV",
}

export default DownloadButton;
