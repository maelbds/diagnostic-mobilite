import React, { Component } from 'react';

class LegendCursor extends React.Component {
  render() {
    return(
      <div className="row mb-1 mt-1">
        <div className="col">
            <div className="row align-items-center">

              <div className="col-4 pr-0 pl-0">
              </div>

              <div className="col-8 pl-0 pr-0">
              <form>
                <div class="form-group mb-0 mt-1">
                  <input onChange={(e) => this.props.cursorFunction(e.target.value)}
                  type="range" class="custom-range" min={this.props.min} max={this.props.max} step={this.props.step} id={"cursor_"+this.props.id} value={this.props.value} />
                </div>
              </form>
              </div>

            </div>
        </div>
      </div>
    )
  }
}

export default LegendCursor;
