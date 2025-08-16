type
  Mesh = object
    vertices: seq[array[3, float]]
    elements: seq[array[3, int]]  # assuming triangles

proc loadGmshMesh(filename: string): Mesh =
  var mesh: Mesh
  var lines = readFile(filename).splitLines()
  var i = 0

  while i < lines.len:
    case lines[i]
    of "$Nodes":
      inc i
      let numNodes = parseInt(lines[i])
      inc i
      for _ in 0..<numNodes:
        let parts = lines[i].split()
        mesh.vertices.add([parseFloat(parts[1]), parseFloat(parts[2]), parseFloat(parts[3])])
        inc i
    of "$Elements":
      inc i
      let numElements = parseInt(lines[i])
      inc i
      for _ in 0..<numElements:
        let parts = lines[i].split()
        if parts[1] == "2":  # triangle
          mesh.elements.add([
            parseInt(parts) - 1,
            parseInt(parts) - 1,
            parseInt(parts) - 1
          ])
        inc i
    else:
      inc i
  return mesh
