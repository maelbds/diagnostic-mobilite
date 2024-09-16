import React, { Component } from 'react';


class Banner extends React.Component {

  render() {
    return(
      <div className="row mb-4">
        <div className="col disclaimer p-2" style={{backgroundColor: this.props.color + "99", borderColor: this.props.color}}>
          <p className="mb-1 mt-1">{this.props.message}</p>
        </div>
      </div>
    )
  }
}

export default Banner;
