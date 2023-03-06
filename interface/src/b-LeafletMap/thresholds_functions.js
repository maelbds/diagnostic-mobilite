import * as ss from "simple-statistics";

import {formatFigure} from '../f-Utilities/util_func';

export function getRange(mode, values, split_nb){
  let range;
  let range_labels = [];
  split_nb = Math.min(split_nb, [...new Set(values)].length)

  function compute_round_threshold(a, b){
    let amplitude = b-a
    let round_nb = 10 ** (Math.round(amplitude).toString().length - 1)
    let mean = (a+b)/2
    mean = Math.round(mean/round_nb)*round_nb
    return mean
  }

  function compute_round_min_max(min, max){
    let amplitude = max-min
    let round_nb = 10 ** (Math.round(amplitude).toString().length - 1)
    let round_min = Math.floor(min/round_nb)*round_nb
    let round_max = Math.ceil(max/round_nb)*round_nb
    return [round_min, round_max]
  }

  function format_range_labels(a, b){
    if (a == b) return formatFigure(a, 3)
    else return formatFigure(a, 3) + " - " + formatFigure(b, 3)
  }

  if(mode == "revenues_median"){
    range = [ [0, 1600],
              [1600, 1700],
              [1700, 1828],
              [1828, 1900],
              [1900, 2000],
              [2000, 10000]
            ]
    range_labels = [
      "moins de 1600",
      "1600 - 1700",
      "1700 - 1828",
      "1828 - 1900",
      "1900 - 2000",
      "plus de 2000"
    ]
  }

  else if(mode == "revenues_mean"){
    range = [ [0, 1580],
              [1580, 1700],
              [1700, 1810],
              [1810, 1926],
              [1926, 2080],
              [2080, 10000] ] // respect des quantiles à l'échelle nationale (carreaux de 1km) cf statistiques-locales
    range = [ [0, 1600],
              [1600, 1750],
              [1750, 1926],
              [1926, 2050],
              [2050, 2200],
              [2200, 10000] ]
    range_labels = [
      "moins de 1600",
      "1600 - 1750",
      "1750 - 1926",
      "1926 - 2050",
      "2050 - 2200",
      "plus de 2200"
    ]
  }

  else if(mode == "gini"){
      range = [ [0, 0.23],
                [0.23, 0.26],
                [0.26, 0.29],
                [0.29, 0.32],
                [0.32, 0.35],
                [0.35, 1]
              ]
      range_labels = [
        "moins de 0,23",
          "0,23 - 0,26",
          "0,26 - 0,29",
          "0,29 - 0,32",
          "0,32 - 0,35",
          "plus de 0,35",
      ]
    }

    else if(mode == "d1/9"){
        range = [ [0, 2.6],
                  [2.6, 3],
                  [3, 3.4],
                  [3.4, 3.8],
                  [3.8, 4.2],
                  [4.2, 20]
                ]
        range_labels = [
          "moins de 2,6",
            "2,6 - 3,0",
            "3,0 - 3,4",
            "3,4 - 3,8",
            "3,8 - 4,2",
            "plus de 4,2",
        ]
      }

  else if(mode == "fuel"){
      range = [ [0, 9],
                [9, 11],
                [11, 13.8],
                [13.8, 17],
                [17, 20],
                [20, 1000]
              ]
      range_labels = [
          "moins de 9",
          "9 - 11",
          "11 - 13.8",
          "13.8 - 17",
          "17 - 20",
          "plus de 20",
      ]
    }

  else if(mode == "fuel_housing"){
      range = [ [0, 12],
                [12, 16],
                [16, 20.3],
                [20.3, 24],
                [24, 28],
                [28, 1000]
              ]
      range_labels = [
          "moins de 12",
          "12 - 16",
          "16 - 20.3",
          "20.3 - 24",
          "24 - 28",
          "plus de 28",
      ]
    }

    else if(mode == "gridded_pop_hh"){
        range = [ [1, 2],
                  [2, 2.2],
                  [2.2, 2.4],
                  [2.4, 2.6],
                  [2.6, 2.8],
                  [2.8, 1000]
                ]
        range_labels = [
            "1.0 - 2.0",
            "2.0 - 2.2",
            "2.2 - 2.4",
            "2.4 - 2.6",
            "2.6 - 2.8",
            "plus de 2.8",
        ]
      }
      else if(mode == "gridded_pop_hh_surf"){
          range = [ [1, 20],
                    [20, 30],
                    [30, 38],
                    [38, 50],
                    [50, 60],
                    [60, 1000]
                  ]
          range_labels = [
              "moins de 20",
              "20 - 30",
              "30 - 38",
              "38 - 50",
              "50 - 60",
              "plus de 60",
          ]
        }

  else if (mode == "work_ratio"){
    range = [ [0, 35],
              [35, 65],
              [65, 100],
              [100, 150],
              [150, 200],
              [200, 10000]
            ]
    range_labels = [
      "moins de 35",
      "35 - 65",
      "65 - 100",
      "100 - 150",
      "150 - 200",
      "plus de 200"
    ]
  }
  else{
    let clusters = ss.ckmeans(values, split_nb)
    range = clusters.map((c)=>[c.slice(0, 1)[0], c.slice(-1)[0]])
    let thresholds_simple = []
    for (let i=0; i<range.length-1; i++){
      thresholds_simple.push(compute_round_threshold(range[i][1], range[i+1][0]))
    }
    let [min, max] = compute_round_min_max(range[0][0], range[range.length-1][1])
    thresholds_simple.unshift(min)
    thresholds_simple.push(max)

    for (let i=0; i<thresholds_simple.length-1; i++){
      range_labels.push(format_range_labels(thresholds_simple[i], thresholds_simple[i+1]))
    }
  }
  return [range, range_labels]
}

export function rangeToThresholds(range){
  return range.slice(1).map((a)=>a[0])
}
