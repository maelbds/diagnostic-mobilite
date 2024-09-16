

export const Filter = class {
  constructor(args){
    this.name = args.name
    this.title = "title" in args ? args.title : null
    this.init = args.init
    this.labels = args.labels
    this.legend = args.legend
  }

  updateFilter(prev_selected, selection){
    let new_selected;

    if(Array.isArray(prev_selected)){
      if(prev_selected.includes(selection)){
        new_selected = prev_selected.filter(c=> c !== selection).sort((a, b) => Object.keys(this.labels).indexOf(a) - Object.keys(this.labels).indexOf(b))
      } else {
        new_selected = prev_selected.concat([selection]).sort((a, b) => Object.keys(this.labels).indexOf(a) - Object.keys(this.labels).indexOf(b))
      }
      if (new_selected.length === 0){
        new_selected = [selection]
      }
    }
    else {
      new_selected = selection;
    }

    return {[`selected_filter_${this.name}`]: new_selected}
  }

  initFilter(parent){
    this.parent = parent
    return {[`selected_filter_${this.name}`]: this.init}
  }




}


export function createFilterObject(filters){
  return {
     selected: Object.fromEntries(filters.map(f=>[f.name, this.state[`selected_filter_${f.name}`]])),
     updateFilter: Object.fromEntries(filters.map(f=>[f.name, this.updateFilter(f)]))
    }
}

export function getFiltersFromIndicators(indicators){
  let all_filters = indicators.map(ind => ind.filters).flat()
  all_filters = all_filters.filter((f, i) => all_filters.indexOf(f) === i)
  return all_filters
}
