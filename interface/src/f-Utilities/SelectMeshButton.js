import React from 'react';

class SelectMeshButton extends React.Component {

  render() {
    return(
      <div className="col-auto">
        <div className="btn-group select_mesh_btn" role="group">
          {this.props.meshesSet.meshes.map(k=>
              <button type="button"
                 key={k.type}
                 onClick={this.props.updateMesh.bind(this, k)}
                 className={this.props.selected_mesh.type === k.type ? "btn active p-1 pl-2 pr-2" : "btn p-1 pl-2 pr-2"}><p>{k.label}</p></button>
          )}
        </div>
      </div>
    )
  }
}

export default SelectMeshButton;
