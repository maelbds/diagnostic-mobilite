import React from 'react';

import PerimeterMap from '../i-Map/PerimeterMap';


class Perimeter extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount(){
    let geometry = this.props.geometry
    let geo = {
      mesh_lines: geometry.com.mesh_lines,
      mesh_outline: geometry.com.mesh_outline,
      mesh: geometry.com.mesh,
      perimeter: geometry.perimeter,
    }

    let custom_map = this.custom_map = new PerimeterMap(this.props.map_id, this.props.styles, geo)
    this.setState({custom_map: custom_map})
  }

  render() {
    return(
        <div id={this.props.map_id} className="map_container" style={{height: "500px", width: "100%"}} />
    )
  }
}

export default Perimeter;
