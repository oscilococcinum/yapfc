from typing import overload
import vtk
import meshio


class Mesh():
    def __init__(self, fpath: str) -> None:
        self._mesh: vtk.vtkUnstructuredGrid = self._loadMesh(fpath)
        self._actor: vtk.vtkActor = self._MapGridToActor(self._mesh)
        self._setColors()
        self._cellData: vtk.vtkCellData = self._loadCellData()
        self._cellColors: vtk.vtkDataArray = self._loadCellColors()

    #Getters
    def getMesh(self) -> vtk.vtkUnstructuredGrid:
        return self._mesh
    
    def getActor(self) -> vtk.vtkActor:
        return self._actor

    def getCellData(self) -> vtk.vtkCellData:
        return self._cellData
    
    def getCellColors(self) -> vtk.vtkDataArray:
        return self._cellColors

    def getCellColor(self, id: int) -> tuple[float, float, float]:
        return self._cellColors.GetTuple3(id)

    def getNodeCoords(self, id: int) -> tuple[float, float, float]:
        return self._mesh.GetPoint(id)

    #Setters
    def setCellColor(self, id: int, color: tuple[float, float, float]) -> None:
        self._cellColors.SetTuple3(id, *color)
        self._cellColors.Modified()

    #Other
    def update(self) -> None:
        self._cellColors.Modified()

    #Internal
    def _loadMesh(self, fpath: str) -> vtk.vtkUnstructuredGrid:
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
        else:
            print(f'This format is not yet implemented')
            return vtk.vtkSTLReader().GetOutput()

    def _MapGridToActor(self, grid: vtk.vtkUnstructuredGrid | None) -> vtk.vtkActor:
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
        mesh.GetCellData().SetActiveScalars('CellColors')

    def _loadCellData(self) -> vtk.vtkCellData:
        return self._mesh.GetCellData()
    
    def _loadCellColors(self) -> vtk.vtkDataArray:
        return self._cellData.GetScalars('CellColors')