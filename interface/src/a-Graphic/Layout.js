import {c_gradient_reds, c_gradient_greens, c_red, c_orange,
  c_green, c_blue, c_yellow, c_light, c_dark, c_violet, c_public_transport} from '../a-Graphic/Colors';


// map ratio

export const map_ratio = window.screen.width <769 ? 5/3 : 3.5/5
export const layout_ratio = window.screen.width <769 ? 11/12*10/12 : 11/12 * 9/12 * 10/12

// map_layout

export const strokeWidth = 1

// ----- places

export const p_size_0 = 6
export const p_size_1 = 10
export const p_size_2 = 16
export const p_size_3 = 22
export const p_size_4 = 28
export const p_size_5 = 34

// ------ routes

export const r_size_1 = 2.5

// ------ white zones

export const wz_size = 20
export const wz_color_limit1 = c_gradient_reds[1]
export const wz_color_limit2 = c_gradient_reds[3]


// ------- work_flows

export const pattern_flows = {
  colors: c_gradient_reds,
  strokes: [3, 4, 5, 6, 7],
  radius: [15, 20, 25, 30, 35]
}


// ------- public_transport

export const pattern_routes_pt = {
  colors: c_public_transport,
  strokeWidth: 2,
  strokeDasharray: "none",
  whiteOutline: true,
}

export const pattern_railways = {
  colors: ["black"],
  strokeWidth: 2,
  strokeDasharray: "8 4 2 4",
  whiteOutline: true,
}

export const pattern_stops_pt = {
  color: c_yellow,
  radius: 2.2,
}

export const pattern_train_stations = {
  color: c_orange,
  radius: 3.5,
}


// activities and services

export const pattern_cluster_0 = {
  color: c_yellow,
  radius: 6,
}

export const pattern_cluster_1 = {
  color: c_gradient_reds[1],
  radius: 9,
}

export const pattern_cluster_2 = {
  color: c_gradient_reds[3],
  radius: 12,
}

// schools

export const pattern_school_0 = {
  color: c_yellow,
  radius: 5,
}

export const pattern_school_1 = {
  color: c_gradient_reds[1],
  radius: 7,
}

export const pattern_school_2 = {
  color: c_gradient_reds[2],
  radius: 9,
}

export const pattern_school_3 = {
  color: c_gradient_reds[3],
  radius: 11,
}

export const pattern_school_4 = {
  color: c_gradient_reds[4],
  radius: 13,
}

// health

export const pattern_health_doc = {
  color: c_yellow,
  radius: 6,
}

export const pattern_health_pharma = {
  color: c_gradient_reds[1],
  radius: 6,
}

export const pattern_health_hospital = {
  color: c_gradient_reds[3],
  radius: 12,
}

// grocery

export const pattern_grocery_conv = {
  color: c_yellow,
  radius: 6,
}

export const pattern_grocery_super = {
  color: c_gradient_reds[1],
  radius: 9,
}

export const pattern_grocery_hyper = {
  color: c_gradient_reds[3],
  radius: 12,
}




// ------- cycle_path

export const pattern_dedicated_cycle_paths = {
  colors: [c_orange], // c_gradient_greens[3],
  strokeWidth: 2,
  strokeDasharray: "none",
  whiteOutline: false,
}

export const pattern_shared_cycle_paths = {
  colors: [c_orange], //c_gradient_greens[2],
  strokeWidth: 1.2,
  strokeDasharray: "2 4",
  whiteOutline: false,
}

export const pattern_cycle_parkings = {
  color: c_yellow,
  radius: 2.5,
}

// ------------- IRVE
export const pattern_irve = {
  color: c_blue,
  radius: 5,
}

// ------------- BNLC
export const pattern_bnlc = {
  color: c_orange,
  radius: 5,
}


// -------------- ZFE

export const pattern_zfe = {
  colors: [c_violet],
  strokeWidth: 4,
  strokeDasharray: "none",
  whiteOutline: true,
}

// -------------- Perimeter

export const pattern_perimeter = {
  "color": c_dark, // "#998B85",
  "width": 1.5,
  "dashArray": "2 4",
  "legend_style": "solid",
}

export const pattern_epci = {
  "color": c_orange,
  "width": 2.5,
  "dashArray": null,
  "legend_style": "solid",
}

export const pattern_arr = {
  "color": c_blue,
  "width": 2.5,
  "dashArray": null,
  "legend_style": "solid",
}

export const pattern_petr = {
  "color": c_green,
  "width": 2.5,
  "dashArray": null,
  "legend_style": "solid",
}

export const pattern_pnr = {
  "color": c_violet,
  "width": 2.5,
  "dashArray": null,
  "legend_style": "solid",
}

export const pattern_pole_emploi = {
  "color": c_orange,
  "width": 2.5,
  "dashArray": null,
  "legend_style": "solid",
}
