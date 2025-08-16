from PySide6.QtWidgets import QVBoxLayout, QDialog, QTextEdit, QPushButton
from PySide6.QtGui import QStandardItem
from vtk import vtkUnstructuredGrid, vtkCellArray, vtkPoints, vtkTetra, VTK_TETRA, vtkDataSetMapper, vtkActor
import meshio


class TextEditor(QDialog):
    def __init__(self, writer):
        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(writer.get_text())
        self.layout.addWidget(self.text_edit)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_text)
        self.layout.addWidget(self.save_button)

    def save_text(self):
        text = self.text_edit.toPlainText()
        self.writer.set_text(text)

class Label(QStandardItem):
    def __init__(self, text="Label"):
        super().__init__(text)
        self.setEditable(False)
        self.textLabel = text

    def getTextLabel(self):
        return self.textLabel

class CcxWriter(QStandardItem):
    def __init__(self, text="CcxWriter"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = ""
        self.className = str(type(self)).split(".")[-1].split("Sub")[0]
        self.textLabel = self.className

    def doubleClicked(self):
        self.editor = TextEditor(self)
        self.editor.exec()

    def set_text(self, newText):
        self.stored_text = newText

    def get_text(self):
        return self.stored_text

    def getTextLabel(self):
        return self.textLabel

class MeshSubWriter(CcxWriter):
    def __init__(self, text="Mesh"):
        super().__init__(text)
        self.setEditable(False)
        self.grid:vtkUnstructuredGrid = None
        self.actor:vtkActor = None
        self.stored_text =""
    
    def load_mesh(self, fpath:str) -> vtkUnstructuredGrid:
        grid:vtkUnstructuredGrid = vtkUnstructuredGrid()
        #mesh: meshio.Mesh = meshio.read(fpath)

        aaa = meshio.Mesh()


        mesh.points

        vtk_points = vtkPoints()
        for i in mesh.points:
            vtk_points.InsertNextPoint(i)

        # Asummes only tetra elements
        cells = mesh.cells_dict["tetra"]
        vtk_cells = vtkCellArray()
        for cell in cells:
            tetra = vtkTetra()
            for i in range(4):
                tetra.GetPointIds().SetId(i, cell[i])
            vtk_cells.InsertNextCell(tetra)

        grid.SetPoints(vtk_points)
        grid.SetCells(VTK_TETRA, vtk_cells)
        self.grid = grid
#        return grid
    
#    def MapGridToActor(self, grid: vtkUnstructuredGrid):
        mapper = vtkDataSetMapper()
        mapper.SetInputData(grid)
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.actor = actor
#        return actor

class MaterialSubWriter(CcxWriter):
    def __init__(self, text="Materials"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = '''
*Material, Name=ABS
*Density
1.02E-09
*Elastic
2000, 0.394
*Expansion, Zero=20
7.4E-05
*Conductivity
0.2256
*Specific heat
1386000000'''

class SectionSubWriter(CcxWriter):
    def __init__(self, text="Sections"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = '''
*Solid section, Elset=Internal_Selection-1_Solid_Section-1, Material=ABS'''

class ConstraintSubWriter(CcxWriter):
    def __init__(self, text="Constraints"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = "**CONSTRAINT"

class ContactSubWriter(CcxWriter):
    def __init__(self, text="Contacts"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = "**CONTACT"

class AmplitudeSubWriter(CcxWriter):
    def __init__(self, text="Amplitudes"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = "**AMPLITUDE"

class InitialConditionSubWriter(CcxWriter):
    def __init__(self, text="Initial Conditions"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = "**INITIALCONDITION"

class StepSubWriter(CcxWriter):
    def __init__(self, text="Step"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = '''
*Step
*Static, Solver=Spooles
*Output, Frequency=1'''

class BoundarySubWriter(CcxWriter):
    def __init__(self, text="Boundary"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = '''
*Boundary, op=New
** Name: Fixed-1
*Boundary
Internal_Selection-1_Fixed-1, 1, 6, 0

*Cload, op=New
*Dload, op=New
** Name: Surface_Traction-1
*Cload
17, 1, 16.6666666666667
22, 1, 33.3333333333333
15, 1, 16.6666666666667
14, 1, 16.6666666666667
18, 1, 16.6666666666667
*Node file
RF, U
*El file
S, E, NOE
**
** End step ++++++++++++++++++++++++++++++++++++++++++++++++
**
*End step'''

class AnalysisSubWriter(CcxWriter):
    def __init__(self, text="Analysis"):
        super().__init__(text)
        self.script: str = f"C:\\Users\\bgawlik\\Desktop\\yapfc\\calculix\\ccx_pastix_exodus.exe {text}"
        self.inp_string: str = ""