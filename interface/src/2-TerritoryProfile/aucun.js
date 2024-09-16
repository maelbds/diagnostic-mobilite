import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


export const aucun = new Indicator({
    indicator: "aucun",
    label: "aucun",

    data_source: null,

    filters: [],

    tables: {},
    layers : {
      choropleth: () => [],
      circle: () => [],
    },

    datasets_names: []
  })
