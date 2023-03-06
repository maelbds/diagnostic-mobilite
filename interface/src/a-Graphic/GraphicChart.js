import React, { Component } from 'react';

import * as colors from './Colors';
import * as layout from './Layout';
import LegendPlace from '../b-LeafletMap/Legend/LegendPlace';

class TerritoryProfile extends React.Component {
  render() {
    return(
      <div className="row mt-5">
        <div className="col">


        <div className="row mb-3">
          <div className="col-12">
            <h1 className="line text-center">Charte graphique</h1>
          </div>
        </div>

          <div className="row mb-3">
            <div className="col-12">
              <h1>titre h1</h1>
            </div>
          </div>

          <div className="row mb-3">
            <div className="col-12">
              <h2>titre h2</h2>
            </div>
          </div>
          <div className="row mb-3">
            <div className="col-12">
              <h3>titre h3</h3>
            </div>
          </div>
          <div className="row mb-3">
            <div className="col-12">
              <h4>titre h4</h4>
            </div>
          </div>
          <div className="row mb-3">
            <div className="col-12">
              <p>paragraphe p <span className="key_figure">chiffre clé</span> <span className="key_figure red-text">chiffre clé rouge</span></p>
            </div>
          </div>

          <div className="row mt-5 mb-4">
              <div className="col-12">
                <p className="mb-3">Echelle séquentielle et divergente (cartes chloroplètes) :</p>
              </div>

          {colors.c_gradient_reds.slice().reverse().concat(colors.c_gradient_greens).map((c) =>


              <div className="col" style={{height: "250px", backgroundColor: c}}>
                <p style={{color: "white"}}>{c}</p>
              </div>
          )}
          </div>


          <div className="row mb-3">
            <div className="col-12">
              <p>Echelles de catégorie :</p>
            </div>
          </div>

          <div className="row mb-4">

              <div className="col-2">
                <div className="row">
                  <div className="col">
                    <p>Général</p>
                  </div>
                </div>
                {Object.values(colors.c_categories).map((c) =>
                    <div className="row m-0 mb-1" style={{height: "50px", backgroundColor: c}}>
                      <p>{c}</p>
                    </div>
                )}
              </div>

              <div className="col-2">
                <p>Marqueurs (lieux, pôles) :</p>
                <LegendPlace label="" color={colors.c_markers[0]} size={layout.p_size_1 *2}/>
                <p className="mb-3">{colors.c_markers[0]}</p>
                <LegendPlace label="" color={colors.c_markers[1]} size={layout.p_size_2 * 2}/>
                <p className="mb-3">{colors.c_markers[1]}</p>
                <LegendPlace label="" color={colors.c_markers[2]} size={layout.p_size_3 * 2}/>
                <p className="mb-3">{colors.c_markers[2]}</p>
                <LegendPlace label="" color={colors.c_markers[3]} size={layout.p_size_4 * 2}/>
                <p className="mb-3">{colors.c_markers[3]}</p>
              </div>

              <div className="col-2">
                <div className="row">
                  <div className="col">
                    <p>Données manquantes</p>
                  </div>
                </div>
                <div className="row m-0" style={{height: "50px", backgroundColor: colors.c_missing_data}}>
                  <p>{colors.c_missing_data}</p>
                </div>
              </div>

              <div className="col-2">
                <div className="row">
                  <div className="col">
                    <p><b>Mobilité</b></p>
                    <p>Modes</p>
                  </div>
                </div>
                {Object.values(colors.c_modes).map((c) =>
                    <div className="row m-0 mb-1" style={{height: "50px", backgroundColor: c}}>
                      <p>{c}</p>
                    </div>
                )}
              </div>

              <div className="col-2">
                <div className="row">
                  <div className="col">
                    <p><b>Mobilité</b></p>
                    <p>Motifs</p>
                  </div>
                </div>
                {Object.values(colors.c_reasons).map((c) =>
                    <div className="row m-0 mb-1" style={{height: "50px", backgroundColor: c}}>
                      <p>{c}</p>
                    </div>
                )}
              </div>

              <div className="col-2">
                <div className="row mb-1">
                  <div className="col">
                    <p><b>Mobilité</b></p>
                    <p>Transport en commun (couleurs claires, plus visibles)</p>
                  </div>
                </div>
                {colors.c_public_transport.map((c) =>
                    <div className="row m-0 mb-1" style={{height: "50px", backgroundColor: c}}>
                      <p>{c}</p>
                    </div>
                )}

                  <div className="row mt-2 mb-1">
                    <div className="col">
                      <p>Ligne de train</p>
                    </div>
                  </div>
                  <div className="row m-0 mb-1" style={{height: "50px", backgroundColor: colors.c_railway}}>
                    <p style={{color: "white"}}>{colors.c_railway}</p>
                  </div>
              </div>

          </div>

          <div className="row mt-5 mb-4">
              <div className="col-12">
              <p className="mb-3"  style={{color: colors.c_red_text}}><b>Red text : {colors.c_red_text}</b></p>
                <p className="mb-3"  style={{color: colors.c_green_text}}><b>Green text : {colors.c_green_text}</b></p>
                <p className="mb-3">Background : {colors.c_background}</p>
              </div>
              <div className="col-6" style={{height: "100px", backgroundColor: colors.c_light}}>
                <p>Light {colors.c_light}</p>
              </div>
              <div className="col-6" style={{height: "100px", backgroundColor: colors.c_dark}}>
                <p style={{color: "white"}}>Dark {colors.c_dark}</p>
              </div>
          </div>


          <div className="row mb-3">
            <div className="col-12">
            <p><a href="https://blog.datawrapper.de/colors-for-data-vis-style-guides/#gradients">guidelines here</a></p>
              <p><a href="https://projects.susielu.com/viz-palette?">check palettes contrasts</a></p>
            </div>
          </div>

        </div>
      </div>
    )
  }
}

export default TerritoryProfile;
