

export const Year = class {
  constructor(args){
    this.name_dataset = args.name_dataset
    this.name_year = args.name_year
    this.years = args.years === null ? [] : args.years

    this.year_selected = this.years.length > 0 ? this.years[this.years.length - 1] : null
  }

  updateSelectedYear(year){
    this.year_selected = year
    return this
  }
}
