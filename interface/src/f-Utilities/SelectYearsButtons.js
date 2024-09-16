import React from 'react';

class SelectYearsButtons extends React.Component {

  render() {
    let {yearsSet, updateYear} = this.props

    let not_null_years = yearsSet.getNotNullYears()
    let not_null_selected_year = not_null_years.map(y => y.year_selected)
    let years_values = not_null_years.map(y => y.years)

    if (years_values.length > 0 && years_values.every(v => v.length === years_values[0].length && v.every((val, i) => val === years_values[0][i]))){
      let year_item = not_null_years[0]
      let selected = not_null_selected_year[0]

      let updateYearAll = (selection) => {
        not_null_years.forEach((y, i) => {
          updateYear(y.name_year,  selection)
        });
      }

      return(
        <div className="col-auto">
          <div className="btn-group select_mesh_btn" role="group">
            {year_item.years.map(y=>
              // year_item.years.length > 1 &&
                <button type="button"
                   key={y+year_item.name_year}
                   onClick={updateYearAll.bind(this, y)}
                   className={selected === y ? "btn active p-1 pl-2 pr-2" : "btn p-1 pl-2 pr-2"}><p>{y}</p></button>
            )}
          </div>
        </div>
      )
    } else {
      return(
        not_null_years.map(year_item =>
          // year_item.years.length > 1 &&
          <div className="col-auto">
            <div className="row no-gutters align-items-center">
                <div className="col">
                <p className="mr-2">{year_item.name_year}</p>
              </div>
              <div className="col-auto">
                <div className="btn-group select_mesh_btn" role="group">
                  {year_item.years.map(k=>
                      <button type="button"
                         key={k+year_item.name_year}
                         onClick={updateYear.bind(this, year_item.name_year,  k)}
                         className={year_item.year_selected === k ? "btn active p-1 pl-2 pr-2" : "btn p-1 pl-2 pr-2"}><p>{k}</p></button>
                  )}
                </div>
              </div>
            </div>
          </div>
      ))
    }
  }
}

export default SelectYearsButtons;
