import vtk


def loadStl(fpath: str) -> vtk.vtkActor():

    """Load the given STL file, and return a vtkActor object for it."""
    # Create a VTK file reader
    reader = vtk.vtkSTLReader()
    reader.SetFileName(fpath)  # Replace with your VTK file path
    reader.Update()

    # Create a mapper for the data
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Create an actor to represent the data
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def polyDataToActor(polydata):
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        # mapper.SetInput(reader.GetOutput())
        mapper.SetInput(polydata)
    else:
        pass
        # mapper.SetInputConnection(polydata.GetProducerPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetColor(0.5, 0.5, 1.0)
    return actor
