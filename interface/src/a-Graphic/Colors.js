// check all colors by displaying the graphic chart, cf App.js

export const c_background = "#fbf9f8";
export const c_light = "#e7e1db";
export const c_map_element_color = "#DACCBE";
export const c_dark = "#252525";

export const c_red_text = "#BB7963";
export const c_green_text = "#6A998A";
export const c_green_text_t = "#6A998Ac9";

export const c_public_transport = ["#DCC2FF", "#9ad5ca", "#d4afb9", "#8DA2E2", "#fbd87f"];
// https://coolors.co/DCC2FF-9ad5ca-d4afb9-8DA2E2-fbd87f
export const c_railway = ["#000"];


export const c_missing_data = "#b5b5b5"

export const c_modes = {
  "voiture": "#5B73C2",
  "voiture passager": "#798DCD",
  "transport en commun": "#FABB77",
  "à pied": "#599B88",
  "vélo": "#71AD9B",
  "moto": "#B98EF1",
  "autre": "#969696",
  "inconnu": c_light,
  "imprécis": c_light,
}
//https://coolors.co/5b73c2-798dcd-fabb77-b98ef1-599b88-71ad9b-969696


export const c_reasons = {
  "domicile ↔ travail": "#5D6698",
  "travail ↔ autre": "#6C78A3",
  "domicile ↔ études": "#9AB3D5",
  "domicile ↔ achats": "#B698DD", // "#D8BBFF",
  "domicile ↔ accompagnement": "#C49A78",
  "domicile ↔ loisirs": "#E0A3A9",
  "domicile ↔ visites": "#FABB77",
  "domicile ↔ affaires personnelles": "#599B88",
  "autre": "#969696",
  "imprécis": c_light,
}
//https://coolors.co/5d6698-6c78a3-9ab3d5-b698dd-c49a78-e0a3a9-fabb77-599b88

export const c_gradient_reds = ["#edd0aa", "#e69b69", "#ca633f", "#a53a22", "#612919"]; // https://coolors.co/edd0aa-e69b69-ca633f-a53a22-612919-96331d
//export const c_gradient_reds = ["#edd0aa", "#e79f70", "#d57148", "#ab4a30", "#8b2814"]; // ORIGINAL https://coolors.co/edd0aa-e79f70-d57148-ab4a30-8b2814

export const c_gradient_greens = ["#cad2c5", "#92b399", "#5b867b", "#405c63", "#29353d"]; // https://coolors.co/cad2c5-92b399-5b867b-405c63-29353d
//export const c_gradient_greens = ["#cad2c5", "#84a98c", "#52796f", "#354f52", "#2f3e46"]; ORIGINAL // https://coolors.co/cad2c5-84a98c-52796f-354f52-2f3e46
export const c_gradient_reds_greens = c_gradient_reds.slice().reverse().concat(c_gradient_greens)


export const c_yellow = "#F6C665";
export const c_orange = "#E69B69";
export const c_green = "#92b399";//"#4e8d67";
export const c_grey_violet = "#C1A79D";//"#4e8d67";
export const c_blue = "#8CA7D9"
export const c_violet = "#8B87D4";
export const c_red = "#B9919F";
// https://coolors.co/f6c665-e69b69-b9919f-8b87d4-8ca7d9-92b399
// PREVIOUS ONE https://coolors.co/F6C665-5a9685-f0ab70-5c6dad-866bcc-A3574B-e7e1db

export const c_selection_zones = c_gradient_greens.slice(1, -1)
export const c_markers = [c_yellow].concat(c_gradient_reds.slice(1)); // for places https://coolors.co/ffce47-e79f70-d57148-ab4a30-8b2814
export const c_categories = [c_yellow, c_orange, c_red, c_violet, c_grey_violet, c_blue, c_green, c_light]; // for plots https://coolors.co/7fa384-98bd8c-628867-9fbda5-6a9471
export const c_zones = [c_light, c_yellow].concat(c_gradient_reds.slice(1))
export const c_direct_indirect = [c_yellow, c_orange, c_light]
export const c_services = [c_yellow, c_orange, c_green, c_grey_violet, c_blue, c_violet, c_red].concat(c_public_transport);
export const c_railway_station = c_red;

export const c_aac = [["F3F2F0", "#F5F0AF", "#EDE049", "#FFB520", "#EE9008", "#EE9008"],
                      ["F3F2F0", "#F6B7C2", "#F15D7D", "#E40038", "#A91535", "#A91535"]];
// Conventionnal colours by INSEE





// Palette map
/*
background : fbf9f8

ocs vegetation #F3F2EA
ocs vegetation canne à sucre #F6F0F2
ocs mangrove/marais #F0F4F2

mer #DBE1ED
mer lighter #E7EAF2
mer lighter2 #EFF0F5

zone batie #F4F0E9

hydro #EBEDF3
zone d'activité #F7F2E9

routes :
fond: white
contour : #E7E1DB


*/
