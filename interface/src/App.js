import React, { Component } from 'react';

import LZString from 'lz-string';
import * as d3 from 'd3';

import Header from './f-Utilities/Header';
import Selection from './0-Home/Selection';
import Diagnostic from './0-Home/Diagnostic';

import {setCookie, getCookie} from './f-Utilities/util_func';


class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      graphic_chart: false, // to display the graphic chart at the end of the visualisation page

      form_banner_link: "https://framaforms.org/usage-diagnostic-mobilite-1715353403", // "https://docs.google.com/document/d/11Jn_Rh6tXPrY9BIZDI3AbWVR2ApEpVbBGRhMyRxDGxE/edit?usp=sharing",//"https://docs.google.com/document/d/1l8lKlkGe3ELZQBh3FvhtHEPuR2-uQam8TlzkN3U0TcQ/edit?usp=sharing", // "https://forms.gle/ZKigEuXA26gLLZTs6", // to display a fixed banner at the end of the page with link to form
      form_banner_label: "Est-ce que ce diagnostic vous a été utile ?", // "Lien vers le référentiel de l'expérimentation"

      form_chart_active: true,

      emd: {emd_added: [], emd_not_added: []},

      error: null,
      isLoaded: false,

      selection: null,
    };
  }

  linkToSelection = (title, geo_codes, zones) => {
    let compressed = LZString.compressToEncodedURIComponent(JSON.stringify({
      name: title,
      geo_codes: geo_codes,
      zones: zones
    }))

    this.setState({
      selection: {
        name: title,
        geo_codes: geo_codes,
        zones: zones
      }
    })

    //window.location.pathname = `/?${compressed}`
  }

  resetSelection = () => {
    this.setState({
      selection: null
    })
  }

  setFormChart = (state) => {
    this.setState({form_chart_active: state})
  }

  componentDidMount(prevProps, prevState) {
      if (getCookie("formChartSet") === null){
        setCookie("formChartSet", "true", 7 * 2)
        this.setState({form_chart_active: true })
      } else {
        this.setState({form_chart_active: false })
      }

      let cog = "2023"

      const font = new FontFace("Source Sans Pro", "url(https://fonts.gstatic.com/s/sourcesanspro/v22/6xK3dSBYKcSV-LCoeQqfX1RYOo3qOK7l.woff2)", {weight: 400});

      Promise.all([
          d3.json(`geography/${cog}/topo_com_with_attr.json`),
          d3.json(`geography/${cog}/topo_com_with_attr_light.json`),

          d3.csv(`geography/${cog}/communes_attr.csv`),
          d3.csv(`geography/${cog}/epci_attr.csv`),
          d3.csv(`geography/${cog}/arrondissements_attr.csv`),
          d3.csv(`geography/${cog}/departements_attr.csv`),
          d3.csv(`geography/${cog}/regions_attr.csv`),
          d3.csv(`geography/${cog}/aav_attr.csv`),

          d3.json(`geography/${cog}/emd.json`),

          d3.json("tiles_style/custom_epure.json"),
          d3.json("tiles_style/custom_names.json"),
          font.load()
      ]).then((files) => {
          this.setState({
            isLoaded: true,

            com_topo: files[0],
            com_topo_light: files[1],

            communes_attr: d3.index(files[2], (d) => d.geo_code),
            // with attributes : geo_code, name, arr, dep, reg, epci, aav, cate_aav, cheflieu_x2154, cheflieu_y2154, typo_aav (computed to fill our needs cf Python file)
            epci_attr: d3.index(files[3], (d) => d.epci),
            // with attributes : epci, epci_name
            arr_attr: d3.index(files[4], (d) => d.arr),
            // with_attributes : arr, arr_chef_lieu (geo_code commune chef-lieu), arr_name
            dep_attr: d3.index(files[5], (d) => d.dep),
            // with_attributes : dep, dep_chef_lieu (geo_code commune chef-lieu), dep_name
            reg_attr: d3.index(files[6], (d) => d.reg),
            // with_attributes : reg, reg_chef_lieu (geo_code commune chef-lieu), reg_name
            aav_attr: d3.index(files[7], (d) => d.aav),
            // with_attributes : aav, aav_name, aav_type
            emd: files[8],

            style_epure: files[9],
            style_names:  files[10],
          });

      }).catch((err) => {
          console.log(err)
            this.setState({
              isLoaded: true,
              error: err
            });
      })
  }

  componentWillUnmount(){
    console.log("unmount")
    this.setState({
      isLoaded: false,
      com_topo: null,
      style_epure: null,
      style_names: null,
    })
  }

  render() {
    /*let test_uri = "N4IgdghgtgpiBcIDCSAEAJCBXALqgahADaoAmMqAygBcBuATnADQgDmMA9gPoDGH5AZwQBtEAHYAnACYxABhAtJARiUAWBeIlKAHBI2SAzEr2KJB2VP3TtBqzIBsdo1aVTtV2dsenZq9z6l1APlTI29Nc1tTQPDJKVklD1VLANsAXRYALw4wGCF4YSkmIoMmUvKyyorqqtrytIBfIA"

    let uri = window.location.pathname.replace("/", "")
    let selection = null
    try {
      let decompressed = LZString.decompressFromEncodedURIComponent(uri)
      selection = JSON.parse(decompressed)
    } catch {}
    let is_selected = selection !== null && "geo_codes" in selection */


    const {graphic_chart, form_banner_link, form_banner_label, form_chart_active,
      com_topo, com_topo_light,
      communes_attr, epci_attr, arr_attr, dep_attr, reg_attr, aav_attr, emd,
      style_epure, style_names,
      isLoaded, error, selection} = this.state;

    let is_selected = selection !== null && "geo_codes" in selection


    let data_selection_map = {
      topology_light: com_topo_light,
      communes_attr: communes_attr,
      epci_attr: epci_attr,
      arr_attr: arr_attr,
      dep_attr: dep_attr,
      reg_attr: reg_attr,
      aav_attr: aav_attr,
      communes_with_emd_added: emd.emd_added,
      communes_with_emd_not_added: emd.emd_not_added
    }

    if (isLoaded & error === null){
      if (is_selected){
      return <Diagnostic name={selection.name}
                         geo_codes={selection.geo_codes}
                         zones={selection.zones}
                         graphic_chart={graphic_chart}
                         form_banner_link={form_banner_link}
                         form_banner_label={form_banner_label}
                         form_chart_active={form_chart_active}
                         setFormChart={this.setFormChart}
                         styles={{style_epure: style_epure, style_names: style_names}}
                         com_topo={com_topo}
                         communes_attr={communes_attr} epci_attr={epci_attr}
                         resetSelection={this.resetSelection}/>
      } else {
      return <Selection loadTerritory={this.linkToSelection}
                        form_banner_link={form_banner_link}
                        form_banner_label={form_banner_label}
                        data_selection_map={data_selection_map}
                        />
      }
    } else if (isLoaded & error !== null){
      return <p>Une erreur est survenue : {error}</p>
    } else {
      return (
        <div className="row">
          <div className="col">

            <Header/>

            <div className="row mt-5">
            </div>

            <div className="row justify-content-center mt-5">
              <div className="col-auto">
                <div class="spinner-grow" role="status">
                  <span class="sr-only">Loading...</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      )
    }

  }
}

export default App;
