import vtk
import meshio


class Mesh():
    def __init__(self, fpath) -> None:
        self.mesh: (vtk.vtkUnstructuredGrid or vtk.vtkPolyData) = self.LoadMesh(fpath)
        self.actor: vtk.vtkActor = self.MapGridToActor(self.mesh)
        # self.inp_mesh =

    def LoadMesh(self, fpath: str) -> vtk.vtkUnstructuredGrid:
        if fpath.endswith(".msh"):
            mesh: meshio.mesh = meshio.read(fpath)

            vtk_points: vtk.vtkPoints = vtk.vtkPoints()
            for i in mesh.points:
                vtk_points.InsertNextPoint(i)

            # Asummes only tetra elements
            cells: mesh.cells_dict = mesh.cells_dict["tetra"]
            vtk_cells: vtk.vtkCellArray = vtk.vtkCellArray()
            for cell in cells:
                tetra = vtk.vtkTetra()
                for i in range(4):
                    tetra.GetPointIds().SetId(i, cell[i])
                vtk_cells.InsertNextCell(tetra)

            grid: vtk.vtkUnstructuredGrid = vtk.vtkUnstructuredGrid()
            grid.SetPoints(vtk_points)
            grid.SetCells(vtk.VTK_TETRA, vtk_cells)
            return grid
        elif fpath.endswith(".stl"):
            reader: vtk.vtkSTLReader = vtk.vtkSTLReader()
            reader.SetFileName(fpath)  # Replace with your VTK file path
            reader.Update()
            grid: vtk.vtkPolyData = reader.GetOutput()
            return grid

    def MapGridToActor(self, grid):
        mapper: vtk.vtkDataSetMapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(grid)
        actor: vtk.vtkActor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor
