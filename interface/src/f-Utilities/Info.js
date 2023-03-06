import React, { Component } from 'react';

class Info extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      popup_position: "left",
    };
  }

  displayPopup = (e) => {
    if (e.clientX < window.innerWidth/2){
      this.setState({
        popup_position: "left",
      })
    } else {
      this.setState({
        popup_position: "right",
      })
    }
  }

  render() {
    return(
      <span className="info_popup" onMouseEnter={this.displayPopup.bind(this)}>i
        <div className={"info_popup_text_"+this.state.popup_position + " p-2 pr-3 pl-3"}>{this.props.content}</div>
      </span>
    )
  }
}

export default Info;
