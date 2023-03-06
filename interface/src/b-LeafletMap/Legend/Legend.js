import React, { Component } from 'react';

import LegendValues from './LegendValues'
import LegendValuesFlows from './LegendValuesFlows'
import LegendLabel from './LegendLabel'
import LegendDescription from './LegendDescription'
import LegendPointMass from './LegendPointMass'
import LegendPlace from './LegendPlace'
import LegendZFE from './LegendZFE'
import LegendCyclePath from './LegendCyclePath'
import LegendRoute from './LegendRoute'
import LegendCursor from './LegendCursor'

import LegendCommune from './LegendCommune'


class Legend extends React.Component {
  render() {
    let legend = this.props.legend

    return(
      <div className="row">
        <div className="col">

            {legend.map((l) =>

                l.type == "LegendValues" ?
                <LegendValues intervals={l.params.intervals}
                              colors={l.params.colors}
                              missing_data={l.params.missing_data}/> :

                l.type == "LegendValuesFlows" ?
                <LegendValuesFlows intervals={l.params.intervals}
                                   colors={l.params.colors}/> :

                l.type == "LegendLabel" ?
                <LegendLabel label={l.params.label} unit={l.params.unit}/> :

                l.type == "LegendCursor" ?
                <LegendCursor min={l.params.min} max={l.params.max} step={l.params.step} value={l.params.value} id={l.params.id} cursorFunction={l.params.cursorFunction}/> :

                l.type == "LegendDescription" ?
                <LegendDescription desc={l.params.desc}/> :

                l.type == "LegendPointMass" ?
                <LegendPointMass label={l.params.label} unit={l.params.unit} color={l.params.color}/> :

                l.type == "LegendPlace" ?
                <LegendPlace label={l.params.label} size={l.params.size} color={l.params.color} subtitle={l.params.subtitle}/> :

                l.type == "LegendCommune" ?
                <LegendCommune label={l.params.label}/> :

                l.type == "LegendCyclePath" ?
                <LegendCyclePath name={l.params.name} pattern={l.params.pattern}/> :

                l.type == "LegendRoute" ?
                <LegendRoute label={l.params.label} color={l.params.color} size={l.params.size}/> :

                l.type == "LegendZFE" ?
                <LegendZFE name={l.params.name} pattern={l.params.pattern}/> :

                l.type == "LegendSpace" ?
                <div className="mt-4"></div> :

                <div></div>

            )}

        </div>
      </div>
    )
  }
}

export default Legend;
