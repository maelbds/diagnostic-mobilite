import {c_gradient_reds, c_gradient_greens, c_violet as c_zfe, c_red, c_orange} from '../a-Graphic/Colors';


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


// ------- cycle_path

export const pattern_dedicated_cycle_paths = {
  "color": c_orange, // c_gradient_greens[3],
  "width": 2,
  "dashArray": null,
  "legend_style": "solid",
}

export const pattern_shared_cycle_paths = {
  "color": c_orange, //c_gradient_greens[2],
  "width": 1.2,
  "dashArray": "2 4",
  "legend_style": "dashed",
}


// -------------- ZFE

export const pattern_zfe = {
  "color": c_zfe,
  "width": 4,
  "dashArray": null,
  "legend_style": "solid",
}
