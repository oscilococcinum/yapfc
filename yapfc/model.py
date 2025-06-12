from PySide6.QtWidgets import QVBoxLayout, QDialog, QTextEdit, QPushButton
from PySide6.QtGui import QStandardItem


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
        self.stored_text ='''
*Node
1, -2.62000000E+001, 5.79483884E+000, -4.82760553E+000
2, -2.62000000E+001, 1.06948388E+001, -4.82760553E+000
3, -1.52000000E+001, 5.79483884E+000, -4.82760553E+000
4, -1.52000000E+001, 1.06948388E+001, -4.82760553E+000
5, -2.62000000E+001, 8.24483884E+000, -4.82760553E+000
6, -2.62000000E+001, 7.01983884E+000, -4.82760553E+000
7, -2.62000000E+001, 9.46983884E+000, -4.82760553E+000
8, -2.62000000E+001, 8.24483884E+000, -2.37760553E+000
9, -2.62000000E+001, 9.46983884E+000, -3.60260553E+000
10, -2.62000000E+001, 7.01983884E+000, -3.60260553E+000
11, -2.07000000E+001, 5.79483884E+000, -4.82760553E+000
12, -2.07000000E+001, 1.06948388E+001, -4.82760553E+000
13, -1.52000000E+001, 8.24483884E+000, -4.82760553E+000
14, -1.52000000E+001, 7.01983884E+000, -4.82760553E+000
15, -1.52000000E+001, 9.46983884E+000, -4.82760553E+000
16, -1.52000000E+001, 8.24483884E+000, -2.37760553E+000
17, -1.52000000E+001, 9.46983884E+000, -3.60260553E+000
18, -1.52000000E+001, 7.01983884E+000, -3.60260553E+000
19, -2.62000000E+001, 8.24483884E+000, -3.60260553E+000
20, -2.07000000E+001, 8.24483884E+000, -4.82760553E+000
21, -2.07000000E+001, 8.24483884E+000, -2.37760553E+000
22, -1.52000000E+001, 8.24483884E+000, -3.60260553E+000

*Element, Type=C3D15, Elset=Solid_part-2
1, 2, 8, 5, 4, 16, 13, 9, 19, 7, 17, 22, 15, 12, 21, 20
2, 1, 5, 8, 3, 13, 16, 6, 19, 10, 14, 22, 18, 11, 20, 21

*Nset, Nset=Internal_Selection-1_Fixed-1
1, 2, 5, 6, 7, 8, 9, 10, 19
*Nset, Nset=Internal-1_Internal_Selection-1_Surface_Traction-1
3, 4, 13, 14, 15, 16, 17, 18, 22

*Elset, Elset=Internal_Selection-1_Solid_Section-1
Solid_part-2
*Elset, Elset=Internal-1_Internal_Selection-1_Surface_Traction-1_S2
1, 2

*Surface, Name=Internal_Selection-1_Surface_Traction-1, Type=Element
Internal-1_Internal_Selection-1_Surface_Traction-1_S2, S2
'''

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