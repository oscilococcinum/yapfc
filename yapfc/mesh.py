from typing import overload
import numpy as np
from vtkmodules.util import numpy_support
import re
import vtk
import meshio
from yapfc.util import timeit
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor 


class Mesh:
    @timeit
    def __init__(self, fpath: str) -> None:
        self._mesh: vtk.vtkUnstructuredGrid = self._loadMesh(fpath)
        self._actor: vtk.vtkActor = self._MapGridToActor(self._mesh)
        self._setColors()
        self._cellData: vtk.vtkCellData = self._loadCellData()
        self._cellColors: vtk.vtkDataArray = self._loadCellColors()

    #Getters
    @timeit
    def getMesh(self) -> vtk.vtkUnstructuredGrid:
        return self._mesh
    @timeit    
    def getActor(self) -> vtk.vtkActor:
        return self._actor
    @timeit   
    def getCellData(self) -> vtk.vtkCellData:
        return self._cellData
    @timeit   
    def getCellColors(self) -> vtk.vtkDataArray:
        return self._cellColors
    @timeit
    def getCellColor(self, id: int) -> tuple[float, float, float]:
        return self._cellColors.GetTuple3(id)
    @timeit
    def getNodeCoords(self, id: int) -> tuple[float, float, float]:
        return self._mesh.GetPoint(id)
    @timeit
    def getCCXNodes(self) -> str:
        nodes = numpy_support.vtk_to_numpy(self._mesh.GetPoints().GetData())
        stream: list[str] = ['*NODE\n']
        for i, (x, y, z) in enumerate(nodes, start=1):
            stream.append(f'{i}, {x:.8E}, {y:.8E}, {z:.8E}\n')
        return ''.join(stream)
    @timeit
    def getCCXElements(self, elset_name: str = "Solid_Part01", one_based: bool = True) -> str:
        """
        Return CCX/Abaqus *Element block for C3D4 (TET4) cells from self._mesh.
        If one_based=True, node IDs are shifted by +1.
        """
        cells = self._mesh.GetCells()
        header = f"*Element, Type=C3D4, Elset={elset_name}"
        lines = [header]

        # --- Fast path (VTK >= 9): use offsets + connectivity ---
        get_offsets = getattr(cells, "GetOffsetsArray", None)
        get_conn = getattr(cells, "GetConnectivityArray", None)
        if callable(get_offsets) and callable(get_conn) and cells.GetOffsetsArray() is not None:
            conn = numpy_support.vtk_to_numpy(cells.GetConnectivityArray())
            offs = numpy_support.vtk_to_numpy(cells.GetOffsetsArray())

            # Optional 1-based conversion
            if one_based:
                # Make a copy only if we need to modify
                conn = conn.astype(conn.dtype, copy=True)
                conn += 1

            append = lines.append
            e = 1
            # offs provides start indices per cell in 'conn'
            for s, t in zip(offs[:-1], offs[1:]):
                nodes = conn[s:t]
                # Expecting TET4 -> length 4; if not, still works generically.
                append(f"{e}, " + ", ".join(map(str, nodes)))
                e += 1

            return "\n".join(lines)

        # --- Legacy path: parse interleaved [n, id, id, ..., n, id, ...] ---
        flat = numpy_support.vtk_to_numpy(cells.GetData())
        n = flat.size
        i = 0
        e = 1
        append = lines.append

        while i < n:
            if i >= n:
                break
            k = int(flat[i])     # number of point IDs in this cell
            i += 1
            if k <= 0 or i + k > n:
                # Malformed cell array; you can raise or break.
                break
            nodes = flat[i:i+k]
            i += k

            if one_based:
                # Copy to Python ints and offset without touching the original array
                append(f"{e}, " + ", ".join(str(int(x) + 1) for x in nodes))
            else:
                append(f"{e}, " + ", ".join(map(str, nodes)))
            e += 1

        return "\n".join(lines)
    @timeit
    def getCCXNodesAndElementsParrarel(self):
        with ThreadPoolExecutor(max_workers=2) as ex:
            fut_a = ex.submit(self.getCCXNodes)
            fut_b = ex.submit(self.getCCXElements)
            # Retrieve results (this waits until done)
            a = fut_a.result()
            b = fut_b.result()
            return a, b

    #Setters
    @timeit
    def setCellColor(self, id: int, color: tuple[float, float, float]) -> None:
        self._cellColors.SetTuple3(id, *color)
        self._cellColors.Modified()
    @timeit
    def update(self) -> None:
        self._cellColors.Modified()

    #Internal
    @timeit
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
    @timeit
    def _MapGridToActor(self, grid: vtk.vtkUnstructuredGrid | None) -> vtk.vtkActor:
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(grid)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor
    @timeit
    def _setColors(self) -> None:
        mesh = self._mesh
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("CellColors")

        for i in range(mesh.GetNumberOfCells()):
                colors.InsertNextTuple3(255, 150, 255)
        
        mesh.GetCellData().SetScalars(colors)
        mesh.GetCellData().SetActiveScalars('CellColors')
    @timeit
    def _loadCellData(self) -> vtk.vtkCellData:
        return self._mesh.GetCellData()
    @timeit
    def _loadCellColors(self) -> vtk.vtkDataArray:
        return self._cellData.GetScalars('CellColors')
    
if __name__ == '__main__':
    mesh = Mesh('C:\\Users\\bgawlik\\OneDrive - Lear Corporation\\Desktop\\yapfc\\testing_data\\hex.msh')
    #[print(i) for i in mesh.getCCXNodes()]
    #[print(i) for i in mesh.getCCXElements()]
    el = mesh.getCCXElements()
    nodes = mesh.getCCXNodes()
    print(el)