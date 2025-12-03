import vtk
import meshio


class Mesh():
    def __init__(self, fpath: str) -> None:
        self.mesh: vtk.vtkUnstructuredGrid | vtk.vtkPolyData | None = self._loadMesh(fpath)
        self.actor: vtk.vtkActor | None = self._MapGridToActor(self.mesh)

    #Getters
    def getMesh(self) -> vtk.vtkUnstructuredGrid | vtk.vtkPolyData | None:
        return self.mesh
    
    def getActor(self) -> vtk.vtkActor | None:
        return self.actor
    
    #Internal
    def _loadMesh(self, fpath: str) -> vtk.vtkUnstructuredGrid | vtk.vtkPolyData | None:
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

    def _MapGridToActor(self, grid: vtk.vtkUnstructuredGrid | vtk.vtkPolyData | None):
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(grid)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor
