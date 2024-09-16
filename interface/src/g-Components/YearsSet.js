

export const YearsSet = class {
  constructor(years){
    this.years = years.length > 1 ? years.filter((y, i) => years.map((d) => d.name_dataset).indexOf(y.name_dataset) === i) : years
  }

  getSelectedYearForDataset(name_dataset){
    let selected = this.years.filter((y) => y.name_dataset === name_dataset)
    if (selected.length === 1){
      return selected[0].year_selected
    } else {
      return null
    }
  }

  getNotNullYears(){
    return this.years.filter((y) => y.years !== null && y.years.length > 0)
  }

  getSelectedYears(){
    return this.years.sort((a, b) => a.name_dataset < b.name_dataset ? 1 : -1).map((y) => y.year_selected).join("-")
  }

  updateYear(name_year, selected_year){
    this.years = this.years.map((y) => y.name_year === name_year ? y.updateSelectedYear(selected_year) : y)
    return this
  }
}
