import React, { Component } from 'react';

import SourcesRow from '../f-Utilities/SourcesRow';

class Table extends React.Component {

  render() {
    return(

    <div className="row">
      <div className="col">

        <div className="row" style={{height: this.props.height, overflow: "auto"}}>
          <div className="col">
            <table className="table table-sm table-hover">
              <thead>
                <tr>
                {this.props.headlines.map((h, i) =>
                  this.props.align[i]=="r" ?
                    <th scope="col" className="text-right pb-1 pt-0">{h}</th> :
                    <th scope="col" className="pb-1 pt-0">{h}</th>
                )}
                </tr>
              </thead>
              <tbody>
              {this.props.rows.map((l) =>
                <tr>
                  {
                    l.map((item, i)=>
                     this.props.align[i]=="r" ?
                       <td className="text-right">{this.props.format[i](item)}</td> :
                       <td>{this.props.format[i](item)}</td>
                  )
                  }
                </tr>
              )}
              </tbody>
            </table>
          </div>
      </div>

      {this.props.all_sources != null &&
      <SourcesRow sources={this.props.all_sources} concerned={this.props.concerned_sources}/>
    }

    </div>
  </div>
    )
  }
}

export default Table;
