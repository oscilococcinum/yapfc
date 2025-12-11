import vtk
import meshio
from copy import copy, deepcopy


class Mesh():
    def __init__(self, fpath: str) -> None:
        self._mesh: vtk.vtkUnstructuredGrid | vtk.vtkPolyData = self._loadMesh(fpath)
        self._actor: vtk.vtkActor = self._MapGridToActor(self._mesh)
        self._setColors()

    #Getters
    def getMesh(self) -> vtk.vtkUnstructuredGrid | vtk.vtkPolyData:
        return self._mesh
    
    def getActor(self) -> vtk.vtkActor:
        return self._actor
    
    #Internal
    def _loadMesh(self, fpath: str) -> vtk.vtkUnstructuredGrid | vtk.vtkPolyData:
        if fpath.endswith(".msh") or fpath.endswith(".mesh"):
            mesh: meshio.Mesh = meshio.read(fpath)

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

            grid = vtk.vtkUnstructuredGrid()
            grid.SetPoints(vtk_points)
            grid.SetCells(vtk.VTK_TETRA, vtk_cells)
            return grid
        elif fpath.endswith(".stl"):
            reader = vtk.vtkSTLReader()
            reader.SetFileName(fpath)  # Replace with your VTK file path
            reader.Update()
            grid = reader.GetOutput()
            return grid
        else:
            print(f'This format is not yet implemented')
            return vtk.vtkSTLReader().GetOutput()

    def _MapGridToActor(self, grid: vtk.vtkUnstructuredGrid | vtk.vtkPolyData | None):
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(grid)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor
    
    def _setColors(self) -> None:
        mesh = self._mesh
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("CellColors")

        for i in range(mesh.GetNumberOfCells()):
                colors.InsertNextTuple3(255, 150, 255)
        
        mesh.GetCellData().SetScalars(colors)
