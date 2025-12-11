from PySide6.QtWidgets import QGridLayout, QComboBox, QVBoxLayout, QDialog, QLabel, QPushButton, QPlainTextEdit, QTextEdit
from PySide6.QtGui import QStandardItem
from copy import copy, deepcopy
from typing import Callable, TypeVar, ParamSpec
from functools import wraps


T = TypeVar("T")
P = ParamSpec("P")

def refOnDemand(fn: Callable[P, T]) -> Callable[P, T]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        want_copy = kwargs.pop("ref", True)
        deep = kwargs.pop("deepCopyRef", True)
        
        result = fn(*args, **kwargs)
        if not want_copy:
            return result
        
        return deepcopy(result) if deep else copy(result)
    
    return wrapper


def CreateComboBox(items: list[str]):
    tmpComboBox:QComboBox = QComboBox()
    tmpComboBox.addItems(items)
    return tmpComboBox

def getTextFromDialog(fields:dict, key:str) -> str:
    widget: QPlainTextEdit | QComboBox = fields[key][1]
    if widget.isEnabled:
        if isinstance(widget, QPlainTextEdit):
            return widget.toPlainText()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        else:
            return 'Object not handled'
    else:
        return ''

class MaterialDialog(QDialog):
    def __init__(self, writer: 'CcxWriter'):
        self.fields:dict = {
                       #Mechanical
                       'Type':[QLabel('Type:'), CreateComboBox(['Elastic', 'Elasto-Plastic', 'Hyperelastic'])],
                       'Hardening':[QLabel('Hardening:'), CreateComboBox(['ISOTROPIC', 'KINEMATIC', 'COMBINED'])],
                       'Hyperelastic model':[QLabel('Hyperelastic model:'), CreateComboBox(['ARRUDA-BOYCE', 'MOONEY-RIVLIN', 'NEO HOOKE', 'OGDEN', 'POLYNOMIAL', 'REDUCED POLYNOMIAL', 'YEOH', 'HYPERFOAM'])], 
                       'Density':[QLabel('Density:'), QPlainTextEdit()],
                       'Young Modulus':[QLabel('Young Modulus:'), QPlainTextEdit()],
                       'Plasitc Strain':[QLabel('Plasitc Strain:'), QPlainTextEdit()],
                       #Thermal
                       'Expansion Coef.':[QLabel('Expansion Coef.:'), QPlainTextEdit()],
                       'Ref. Temp.':[QLabel('Ref. Temp.:'), QPlainTextEdit()],
                       'Expansion Type':[QLabel('Expansion Type:'), CreateComboBox(['ISO', 'ORHTO', 'ANISO'])],
                       'Conductivity':[QLabel('Conductivity'), QPlainTextEdit()],
                       'Specific Heat':[QLabel('Specific Heat:'), QPlainTextEdit()]}
        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)

        self.llayout = QGridLayout(self)
        for i, field in enumerate(self.fields.values()):
            for j, widget in enumerate(field):
                self.llayout.addWidget(widget, i, j)


        self.ok_button = QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.save_text)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)

        lastRow:int = self.llayout.rowCount()
        self.llayout.addWidget(self.cancel_button, lastRow, 0)
        self.llayout.addWidget(self.ok_button, lastRow, 1)

        self.ttype:QComboBox = self.fields['Type'][1]
        self.hardening:QComboBox = self.fields['Hardening'][1]
        self.hyper:QComboBox = self.fields['Hyperelastic model'][1]
        self.ttype.currentTextChanged.connect(self.updateFields)
        self.hardening.currentTextChanged.connect(self.updateFields)
        self.hyper.currentTextChanged.connect(self.updateFields)

        self.updateFields()

    def updateFields(self):
        self.hardening.setEnabled(False)
        self.hyper.setEnabled(False)
        if self.ttype.currentText() == 'PLASTIC':
            self.hardening.setEnabled(True)
        elif self.ttype.currentText() == 'HYPERELASTIC':
            self.hyper.setEnabled(True)

    def save_text(self):
        textArr:list = []
        for item_key in self.fields.keys():
            textArr.append(getTextFromDialog(self.fields, item_key))
        #self.writer.set_text(text)

class TextEditor(QDialog):
    def __init__(self, writer:'CcxWriter'):
        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)

        self.llayout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(writer.getStoredText())
        self.llayout.addWidget(self.text_edit)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_text)
        self.llayout.addWidget(self.save_button)

    def save_text(self):
        text = self.text_edit.toPlainText()
        self.writer.setStoredText(text)

class Label(QStandardItem):
    def __init__(self, text="Label"):
        super().__init__(text)
        self._textLabel = text
        self.setEditable(False)

    # Getters
    @refOnDemand
    def getTextLabel(self):
        return self._textLabel

    # Virtual
    @refOnDemand
    def getStoredText(self) -> str:
        return ''

class CcxWriter(QStandardItem):
    def __init__(self, text="CcxWriter"):
        super().__init__(text)
        self.setEditable(False)
        self._stored_text = ""
        self._className = str(type(self)).split(".")[-1].split("Sub")[0]
        self._textLabel = self._className

    # Actions
    def doubleClicked(self) -> None:
        self.editor = TextEditor(self)
        self.editor.exec()

    # Setters
    def setStoredText(self, newText:str) -> None:
        self._stored_text = newText

    # Getters
    @refOnDemand
    def getStoredText(self) -> str:
        return copy(self._stored_text)
    
    @refOnDemand
    def getTextLabel(self) -> str:
        return self._textLabel

class MeshSubWriter(CcxWriter):
    def __init__(self, text="Mesh"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText('''
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
Internal-1_Internal_Selection-1_Surface_Traction-1_S2, S2''')

class MaterialSubWriter(CcxWriter):
    def __init__(self, text="Materials"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText('''*Material, Name=ABS
*Density
1.02E-09
*Elastic
2000, 0.394
*Expansion, Zero=20
7.4E-05
*Conductivity
0.2256
*Specific heat
1386000000''')

    def doubleClicked(self):
        self.editor = TextEditor(self)
        self.editor.exec()

class SectionSubWriter(CcxWriter):
    def __init__(self, text="Sections"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText('''*Solid section, Elset=Internal_Selection-1_Solid_Section-1, Material=ABS''')

class ConstraintSubWriter(CcxWriter):
    def __init__(self, text="Constraints"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText("**CONSTRAINT")

class ContactSubWriter(CcxWriter):
    def __init__(self, text="Contacts"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText("**CONTACT")

class AmplitudeSubWriter(CcxWriter):
    def __init__(self, text="Amplitudes"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText("**AMPLITUDE")

class InitialConditionSubWriter(CcxWriter):
    def __init__(self, text="Initial Conditions"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText("**INITIALCONDITION")

class StepSubWriter(CcxWriter):
    def __init__(self, text="Step"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText('''
*Step
*Static, Solver=Spooles
*Output, Frequency=1''')

class BoundarySubWriter(CcxWriter):
    def __init__(self, text="Boundary"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText('''*Boundary, op=New
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
*End step''')

class AnalysisSubWriter(CcxWriter):
    def __init__(self, text="Analysis"):
        super().__init__(text)
        self._inp_string: str = ""

    def setInpString(self, newInpStr:str) -> None:
        self._inp_string = newInpStr