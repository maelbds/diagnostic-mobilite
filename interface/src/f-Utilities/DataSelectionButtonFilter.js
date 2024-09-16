import React from 'react';

import {data_source_types} from './data_source';

class DataSelectionButtonFilter extends React.Component {

  render() {
      let {ind, selected_indicator, selected_filters, updateIndicatorAndFilter} = this.props

      return(

      <div className="row">
        <div className="col">

          <div className="row justify-content-between align-items-center">
            <div className="col">

              <p className={ind.indicator === selected_indicator ? "mb-1 mt-1 datalist selected" : "mb-1 mt-1 datalist"}
                 onClick={updateIndicatorAndFilter.bind(this, ind, null, null)} title={"legend" in ind ? ind.legend : null}>
                 {ind.label}
                 <i>{ind.label_i != null && ind.label_i}</i>
                 <span className={"ml-1 material-symbols-outlined " + ind.data_source} title={data_source_types[ind.data_source]}>verified</span></p>

            </div>

            <div className="col-auto">
            </div>
          </div>

          {ind.filters !== undefined && ind.filters.length > 0 && ind.indicator === selected_indicator &&

            ind.filters.map(filter => (
              <div className="row">
                <div className="col">
                  {filter.title !== null && <p><i>{filter.title}</i></p>}

                  <div className="btn-group flex-wrap select_filter_btn mb-2" role="group">
                    {Object.keys(filter.labels).map(k=>
                      Array.isArray(selected_filters[filter.name]) ?
                        <button type="button"
                           key={k}
                           onClick={updateIndicatorAndFilter.bind(this, ind, filter, k)}
                           className={selected_filters[filter.name].includes(k) ? "btn active p-0 pl-2 pr-2" : "btn p-0 pl-2 pr-2"}>
                              <p>{filter.labels[k]}</p>
                        </button> :
                        <button type="button"
                           key={k}
                           onClick={updateIndicatorAndFilter.bind(this, ind, filter, k)}
                           className={selected_filters[filter.name] === k ? "btn active p-0 pl-2 pr-2" : "btn p-0 pl-2 pr-2"}>
                              <p>{filter.labels[k]}</p>
                        </button>
                      )}
                  </div>

                </div>
              </div>
            ))
          }

        </div>
      </div>
    )
  }
}

export default DataSelectionButtonFilter;
