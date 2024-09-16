import {Mesh, meshes_labels} from './Mesh';


const default_mesh_types = Object.keys(meshes_labels)


export const MeshesSet = class {
  constructor(meshes){
    this.meshes = meshes.length > 0 ? meshes : default_mesh_types.map((type) => new Mesh(type))
  }

  getMeshInit(){
    return this.meshes[0]
  }

  includesMesh(mesh){
    return this.meshes.some((m) => m.type === mesh.type)
  }
}

export function createMeshesSetFromTypes(types){
  types = (types === null | types === undefined) ? [] : types
  return new MeshesSet(types.map((type) => new Mesh(type)))
}

export function intersectMeshesSet(sets){
  if (sets.length > 0){
    let meshes = sets.map((s) => s.meshes).reduce((a, b) => a.filter((mesh1) => b.map((mesh2) => mesh2.type).includes(mesh1.type)))
    return new MeshesSet(meshes)
  } else {
    return new MeshesSet([])
  }
}
