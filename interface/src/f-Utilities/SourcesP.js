import React, { Component } from 'react';

class SourcesP extends React.Component {

  render() {
    let sources = this.props.sources
    let concerned = this.props.concerned
    let new_concerned = Array.from(concerned)
    if (concerned.includes("emd")){
      new_concerned.push("analysis")
    }
    if (concerned.includes("entd")){
      new_concerned.push("model")
      new_concerned.push("analysis")
    }

    function handleLink(label, link){
      if (link != undefined & link !=""){
        return <a href={link} target="_blank">{label}</a>
      }
      else{
        return label
      }
    }

    if (concerned.length > 0){
      return(
        <p className="sources">Source{new_concerned.length>1 && "s"} {/*this.props.processed && "(traitement)"*/} :
          {[" "].concat(new_concerned.filter((l)=>Object.keys(this.props.sources).includes(l)).map((l)=>
              handleLink(sources[l].label, sources[l].link)
          ).reduce((prev, curr) => [prev, ' | ', curr]))}
        </p>
      )
    } else {
      return
    }


  }
}

export default SourcesP;
