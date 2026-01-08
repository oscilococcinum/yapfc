from PySide6.QtGui import QStandardItem
from yapfc.dialogs import TextEditor, MaterialDialog, SectionDialog, CCXWriterCategory

class Label(QStandardItem):
    def __init__(self, text="Label"):
        super().__init__(text)
        self._textLabel = text
        self.setEditable(False)

    # Getters
    def getTextLabel(self):
        return self._textLabel

    # Virtual
    def getStoredText(self) -> str:
        return ''

class CcxWriter(QStandardItem):
    writters: list['CcxWriter'] = []
    def __init__(self, text="CcxWriter", dialog: None | type[MaterialDialog | SectionDialog]=None):
        super().__init__(text)
        type(self).writters.append(self)
        self.setEditable(False)
        self._stored_text = ""
        self._className = str(type(self)).split(".")[-1].split("Sub")[0]
        self._textLabel = self._className
        self._editor = TextEditor(self)
        if dialog:
            self.dialog = dialog(self)
        else:
            self.dialog = None

    # Actions
    def doubleClicked(self) -> None:
        if self.dialog != None:
            self.dialog.exec()
        else:
            pass
    def openTextEditor(self) -> None:
        self._editor.exec()

    def removeWriter(self) -> None:
        type(self).writters.remove(self)

    # Setters
    def setStoredText(self, newText:str) -> None:
        self._stored_text = newText

    # Getters
    def getStoredText(self) -> str:
        return self._stored_text
    
    def getTextLabel(self) -> str:
        return self._textLabel
    
    @classmethod
    def getWritersList(cls) -> list['CcxWriter']:
        return cls.writters
    
    @classmethod
    def getWritersListByCategory(cls, cat: CCXWriterCategory) -> list['CcxWriter']:
        result: list[CcxWriter] = []
        for i in cls.writters:
            if i.__class__.__name__ == cat.name:
                result.append(i)
        return result

class MeshSubWriter(CcxWriter):
    def __init__(self, text="Mesh"):
        super().__init__(text)
        self.setEditable(False)
        self.setStoredText('''*Node
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
        super().__init__(text, dialog=MaterialDialog)
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
class SectionSubWriter(CcxWriter):
    def __init__(self, text="Sections"):
        super().__init__(text, dialog=SectionDialog)
        self.setEditable(False)
        self.setStoredText('''*Solid section, Elset=Internal_Selection-1_Solid_Section-1, Material=ABS''')
    
    def doubleClicked(self) -> None:
        if self.dialog:
            self.dialog.updateFields()
        return super().doubleClicked()

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
        self.setStoredText('''*Step
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
