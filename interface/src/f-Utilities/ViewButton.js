import React, { Component } from 'react';

class ViewButton extends React.Component {

  render() {
    return(
        <div className="col-auto pr-0">
          <p onClick={this.props.setView}
             className={this.props.active ? "button p-1 pl-3 pr-3 active" : "button p-1 pl-3 pr-3"}>{this.props.label}</p>
        </div>
    )
  }
}

export default ViewButton;
