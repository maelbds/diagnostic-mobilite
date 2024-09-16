import React from 'react';

class SourcesP extends React.Component {

  render() {
    let selected_sources = this.props.selected_sources
    if (selected_sources.length > 1){
      selected_sources = selected_sources.filter((v, i)=> selected_sources.indexOf(v) === i)
    }

    function handleLink(label, link){
      if (link !== undefined & link !== ""){
        return <a href={link} key={label} target="_blank" rel="noreferrer">{label}  <span className="material-symbols-outlined link">open_in_new</span></a>
      }
      else{
        return label
      }
    }

    if (selected_sources.length > 0){
      return(
        <p className="sources">Source{selected_sources.length > 1 && "s"} :
          {[" "].concat(selected_sources.map((s) =>
              handleLink(s.label, s.link)
          ).reduce((prev, curr) => [prev, ' | ', curr]))}
        </p>
      )
    } else {
      return
    }


  }
}

export default SourcesP;
