import vtk
import numpy as np
import meshio

def get_uns_grid(fpath: str) -> vtk.vtkUnstructuredGrid:
    mesh = meshio.read(fpath)
    
    vtk_points = vtk.vtkPoints()
    for i in mesh.points:
        vtk_points.InsertNextPoint(i)
    
    # Asummes only tetra elements
    cells = mesh.cells_dict["tetra"]
    vtk_cells = vtk.vtkCellArray()
    for cell in cells:
        tetra = vtk.vtkTetra()
        for i in range(4):
            tetra.GetPointIds().SetId(i, cell[i])
        vtk_cells.InsertNextCell(tetra)

    unstructured_grid = vtk.vtkUnstructuredGrid()
    unstructured_grid.SetPoints(vtk_points)
    unstructured_grid.SetCells(vtk.VTK_TETRA, vtk_cells)
    return unstructured_grid

def load_file(fpath: str) -> vtk.vtkActor:
    """Load the given STL file, and return a vtkActor object for it."""
    if fpath.endswith(".stl"):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(fpath)  # Replace with your VTK file path
        reader.Update()
        # Create a mapper for the data
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
    elif fpath.endswith(".msh"):
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(get_uns_grid(fpath))
 
    # Create an actor to represent the data
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor