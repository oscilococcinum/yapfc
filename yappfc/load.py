import vtk


def load_file(fpath: str) -> vtk.vtkActor():
    """Load the given STL file, and return a vtkActor object for it."""
    if fpath.endswith(".stl"):
        reader = vtk.vtkSTLReader()
    elif fpath.endswith(".msh"):
        reader = vtk.vtkGMSHReader()
    reader.SetFileName(fpath)  # Replace with your VTK file path
    reader.Update()

    # Create a mapper for the data
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Create an actor to represent the data
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor
