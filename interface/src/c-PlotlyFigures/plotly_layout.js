import {c_categories as colors} from '../a-Graphic/Colors';

export const layout_pie = {
  font:{family: "source sans pro",
        color: "rgba(0,0,0,1)",
        size: 17},
  paper_bgcolor: "rgba(0,0,0,0)",
  margin: {l:0,
           r:0,
           b:0,
           t:0},
  height: 350,
  autosize: true,
  showlegend: false,
  legend:{
    x: 1,
    y:0.1
  },
  colorway: colors,
  hoverlabel: {
      bgcolor:"rgba(255,255,255,0.1)",
      bordercolor:"rgba(0,0,0,0.1)",
      font: {family: "Source sans pro",
             color:"rgba(0,0,0,1)",
             size: 18}
  },
  uniformtext: {
    minsize: 12,
    mode: "hide"
  }
};

export const layout_bar_stacked = {
  font:{family: "source sans pro",
        color: "rgba(0,0,0,1)",
        size: 18},
  plot_bgcolor: "rgba(0,0,0,0)",
  paper_bgcolor: "rgba(0,0,0,0)",
  yaxis: {
    visible: false,
    showgrid: false,
  },
  margin: {l:0,
           r:0,
           b:0,
           t:0},
  height: 350,
  autosize: true,
  showlegend: false,
  colorway: colors,
  hoverlabel: {
      bgcolor:"rgba(255,255,255,0.1)",
      bordercolor:"rgba(0,0,0,0.1)",
      font: {family: "Source sans pro",
             color:"rgba(0,0,0,1)",
             size: 18},
  },
  barmode: "stack",
};

export const layout_bar = {
  font:{family: "source sans pro",
        color: "rgba(0,0,0,1)",
        size: 18},
  plot_bgcolor: "rgba(0,0,0,0)",
  paper_bgcolor: "rgba(0,0,0,0)",
  yaxis: {
    visible: false,
    showgrid: false,
  },
  margin: {l:0,
           r:0,
           b:30,
           t:0},
  height: 350,
  autosize: true,
  showlegend: false,
  colorway: colors,
  hoverlabel: {
      bgcolor:"rgba(255,255,255,0.1)",
      bordercolor:"rgba(0,0,0,0.1)",
      font: {family: "Source sans pro",
             color:"rgba(0,0,0,1)",
             size: 18},
  },
  barmode: "group",
};
