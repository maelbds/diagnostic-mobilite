import React, { Component } from "react";

import { c_modes } from "../../a-Graphic/Colors";

class LegendModes extends React.Component {
  render() {
    return (
      <div className="row">
        {Object.keys(c_modes)
          .filter((key) => key != "inconnu")
          .map((key, i) => (
              <div className="col-auto pr-0">
                <p>
                  <span
                    className="legend_color_circles align-middle mr-1"
                    style={{ backgroundColor: c_modes[key] }}
                  ></span>
                 {key}</p>
              </div>
          ))}
      </div>
    );
  }
}

export default LegendModes;
