import React from 'react';

import {map_ratio, layout_ratio} from '../a-Graphic/Layout'


class MapElement extends React.Component {
  constructor(props) {
   super(props);
  }

  render() {
    return(
      <div className="row no-gutters">
        <div className="col">
          <div id={this.props.id} className="map_container" style={{height: this.props.height, width: "100%"}}>
          </div>
        </div>
      </div>
    )
  }
}

export default MapElement;


MapElement.defaultProps = {
  height: window.screen.width*layout_ratio*map_ratio + "px",
}
