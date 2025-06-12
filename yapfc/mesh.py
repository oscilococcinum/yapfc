import vtk
import meshio


class Mesh():
    def __init__(self, fpath: str) -> None:
        self.mesh: (vtk.vtkUnstructuredGrid or vtk.vtkPolyData) = self.LoadMesh(fpath)
        self.actor: vtk.vtkActor = self.MapGridToActor(self.mesh)

    def LoadMesh(self, fpath: str) -> (vtk.vtkUnstructuredGrid or vtk.vtkPolyData):
        if fpath.endswith(".msh") or fpath.endswith(".mesh"):
            mesh: meshio.mesh = meshio.read(fpath)

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
            grid: vtk.vtkPolyData = reader.GetOutput()
            return grid

    def MapGridToActor(self, grid: (vtk.vtkUnstructuredGrid or vtk.vtkPolyData)):
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(grid)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor
