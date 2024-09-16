export const meshes_labels = {
  com: "Communes",
  epci: "EPCI"
}

export const Mesh = class {
  constructor(type){
    this.type = type
    this.label = meshes_labels[type]
  }
}
