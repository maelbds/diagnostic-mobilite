import React from 'react';

import SourcesRow from '../f-Utilities/SourcesRow';

import {map_ratio, layout_ratio} from '../a-Graphic/Layout'

class Table extends React.Component {

  render() {
    return(
        <div className="row" style={{height: this.props.height, overflow: "auto"}}>
          <div className="col">
            <table className="table table-sm table-hover">
              <thead>
                <tr>
                {this.props.headlines.map((h, i) =>
                  this.props.align[i]==="r" ?
                    <th scope="col" key={"headline_item"+i} className="text-right pb-1 pt-0"><p><b>{h}</b></p></th> :
                    <th scope="col" key={"headline_item"+i} className="pb-1 pt-0"><p><b>{h}</b></p></th>
                )}
                </tr>
              </thead>
              <tbody>
              {this.props.rows.map((l, id) =>
                <tr key={"line"+id}>
                  {
                    l.map((item, i)=>
                     this.props.align[i]==="r" ?
                       <td key={"line_item"+i} className="text-right">{this.props.format[i](item)}</td> :
                       <td key={"line_item"+i}>{this.props.format[i](item)}</td>
                  )
                  }
                </tr>
              )}
              </tbody>
            </table>
          </div>
      </div>
    )
  }
}

export default Table;

Table.defaultProps = {
  height: window.screen.width*layout_ratio*map_ratio
}
