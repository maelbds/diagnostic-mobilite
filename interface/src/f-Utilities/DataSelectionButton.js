import React, { Component } from 'react';

class DataSelectionButton extends React.Component {

  render() {
    return(
      <p className={this.props.selected ? "mb-2 mt-1 datalist selected" : "mb-2 mt-1 datalist"}
         onClick={this.props.display_category}>{this.props.label} <i>{this.props.label_i != null && this.props.label_i}</i></p>
    )
  }
}

export default DataSelectionButton;
