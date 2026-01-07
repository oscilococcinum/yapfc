import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QRadioButton,
    QComboBox, QPushButton, QLabel, QLineEdit, QGridLayout, QComboBox,
    QVBoxLayout, QDialog, QLabel, QPushButton, QPlainTextEdit, QTextEdit
)
from enum import Enum, StrEnum, auto

#from yapfc.model import CcxWriter


def get_option_from_json(json_file:str, option:str) -> str:
        try:
            with open(f"{json_file}", "r") as f:
                options = json.load(f)
                return options.get(f"{option}", "")
        except:
            raise FileNotFoundError

class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options Dialog")

        layout = QVBoxLayout()

        # Text boxes
        layout.addWidget(QLabel("ccx path:"))
        self.ccx_path = QLineEdit()
        layout.addWidget(self.ccx_path)

        layout.addWidget(QLabel("Paraview path:"))
        self.paraview_path = QLineEdit()
        layout.addWidget(self.paraview_path)

#        # Checkboxes
#        self.checkbox1 = QCheckBox("Enable feature A")
#        self.checkbox2 = QCheckBox("Enable feature B")
#        layout.addWidget(self.checkbox1)
#        layout.addWidget(self.checkbox2)

#        # Radio buttons
#        self.radio1 = QRadioButton("Mode 1")
#        self.radio2 = QRadioButton("Mode 2")
#        layout.addWidget(self.radio1)
#        layout.addWidget(self.radio2)

#        # Combo box
#        layout.addWidget(QLabel("Select profile:"))
#        self.combo = QComboBox()
#        self.combo.addItems(["Default", "Advanced", "Custom"])
#        layout.addWidget(self.combo)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        self.load_options()

    def accept(self):
        self.save_options()
        super().accept()

    def save_options(self):
        options = {
            "ccx_path": self.ccx_path.text(),
            "paraview_path": self.paraview_path.text()
#            "feature_a": self.checkbox1.isChecked(),
#            "feature_b": self.checkbox2.isChecked(),
#            "mode_1": self.radio1.isChecked(),
#            "mode_2": self.radio2.isChecked(),
#            "profile": self.combo.currentText()
        }
        with open("options.json", "w") as f:
            json.dump(options, f)

    def load_options(self):
        try:
            with open("options.json", "r") as f:
                options = json.load(f)
                self.ccx_path.setText(options.get("ccx_path", ""))
                self.paraview_path.setText(options.get("paraview_path", ""))
#                self.checkbox1.setChecked(options.get("feature_a", False))
#                self.checkbox2.setChecked(options.get("feature_b", False))
#                self.radio1.setChecked(options.get("mode_1", False))
#                self.radio2.setChecked(options.get("mode_2", False))
#                profile = options.get("profile", "Default")
#                index = self.combo.findText(profile)
#                if index >= 0:
#                    self.combo.setCurrentIndex(index)
        except FileNotFoundError:
            pass


### Material dialog
def CreateComboBox(items: type[StrEnum]):
    tmpComboBox:QComboBox = QComboBox()
    for i in items:
        tmpComboBox.addItem(i.name)
    return tmpComboBox

def listToText(l: list[str]):
    text: str = ''
    for line in l:
        text += line
    return text

class AnalisysType(StrEnum):
    Elastic = '*ELASTIC'
    ElastoPlastic = '*PLASTIC'
    Hyperelastic = '*HYPERELASTIC'

class HardeningType(StrEnum):
    Isotropic = 'ISOTROPIC'
    Kinematic = 'KINEMATIC'

class HyperelasticType(StrEnum):
    ArrudaBoyce = 'ARRUDA-BOYCE'
    MooneyRivlin = 'MOONEY-RIVLIN'
    NeoHooke = 'NEO HOOKE'
    Ogden = 'OGDEN'
    Polynomial = 'POLYNOMIAL'
    ReducedPolynomial = 'REDUCED POLYNOMIAL'
    Yeoh = 'YEOH'
    Hyperfoam = 'HYPERFOAM'

class ExpansionType(StrEnum):
    Iso = 'ISO'
    Ortho = 'ORTHO'
    Aniso = 'ANISO'

class ComboDialogElement:
    def __init__(self, label: str, comboboxEnum: type[StrEnum], elemntsList: list):
        self.label: QLabel = QLabel(label)
        self.elemntEnum = comboboxEnum
        self.widget: QComboBox = CreateComboBox(comboboxEnum)
        elemntsList.append(self)

    def getValue(self) -> str:
        return self.elemntEnum[self.widget.currentText()]

    def getActiveEnum(self) -> StrEnum:
        return self.elemntEnum[self.widget.currentText()]

    def setValue(self, val: StrEnum):
        self.widget.setCurrentText(val.name)

class TextDialogElement:
    def __init__(self, label: str, elemntsList: list):
        self.label: QLabel = QLabel(label)
        self.widget: QPlainTextEdit = QPlainTextEdit()
        elemntsList.append(self)

    def getValue(self) -> str:
        return self.widget.toPlainText()

    def setValue(self, val: str) -> None:
        self.widget.setPlainText(val)

class MaterialDialog(QDialog):
    def __init__(self, writer: 'CcxWriter'):
        self.elementList: list[ComboDialogElement | TextDialogElement] = []
        elementList = self.elementList
        self.AnalisysType = ComboDialogElement('Type', AnalisysType, elementList)
        self.HardeningType = ComboDialogElement('Hardening', HardeningType, elementList)
        self.ExpansionType = ComboDialogElement('Elastic Expansion Type', ExpansionType, elementList)
        self.HyperelasticType = ComboDialogElement('Hyperelastic Model', HyperelasticType, elementList)
        self.Desnsity = TextDialogElement('Density', elementList)
        self.YoungModulus = TextDialogElement('Young Modulus\nOrtho, Aniso Coef.', elementList)
        self.PlasticStrain = TextDialogElement('Plastic Strain\nHyperelastic Coef.', elementList)
        self.ExpansionCoef = TextDialogElement('Expansion Coef.', elementList)
        self.RefTemp = TextDialogElement('Ref. Temp.', elementList)
        self.Conductivity = TextDialogElement('Conductivity', elementList)
        self.SpecificHeat = TextDialogElement('Specific Heat', elementList)

        self.HardeningType.widget.setEnabled(False)
        self.HyperelasticType.widget.setEnabled(False)

        self.AnalisysType.widget.currentTextChanged.connect(self.updateFields)
        self.HardeningType.widget.currentTextChanged.connect(self.updateFields)
        self.HyperelasticType.widget.currentTextChanged.connect(self.updateFields)
        self.ExpansionType.widget.currentTextChanged.connect(self.updateFields)

        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)

        self.llayout = QGridLayout(self)
        for i, elemnt in enumerate(elementList):
            self.llayout.addWidget(elemnt.label, i, 0)
            self.llayout.addWidget(elemnt.widget, i, 1)

        self.ok_button = QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.save_text)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)

        lastRow:int = self.llayout.rowCount()
        self.llayout.addWidget(self.cancel_button, lastRow, 0)
        self.llayout.addWidget(self.ok_button, lastRow, 1)

        self.updateFields()
        self.setupTestvalues()

    def setupTestvalues(self):
        [i.setValue(j) for i,j  in zip(self.elementList,[AnalisysType.ElastoPlastic,
                                                         HardeningType.Kinematic,
                                                         ExpansionType.Iso,
                                                         HyperelasticType.ArrudaBoyce,
                                                         '1.02e-9',
                                                         '2000, 0.394',
                                                         '40, 0.2',
                                                         '7.4e-5',
                                                         '20',
                                                         '0.2256',
                                                         '1386000000'])]

    def updateFields(self):
        enabled: list[TextDialogElement | ComboDialogElement] = []

        if self.AnalisysType.getActiveEnum() == AnalisysType.Elastic:
            enabled = [self.AnalisysType,
                       #self.HardeningType,
                       self.ExpansionType,
                       #self.HyperelasticType,
                       self.Desnsity,
                       self.YoungModulus,
                       #self.PlasticStrain,
                       self.ExpansionCoef,
                       self.RefTemp, 
                       self.Conductivity,
                       self.SpecificHeat]
        if self.AnalisysType.getActiveEnum() == AnalisysType.ElastoPlastic:
            enabled = [self.AnalisysType,
                       self.HardeningType,
                       self.ExpansionType,
                       #self.HyperelasticType,
                       self.Desnsity,
                       self.YoungModulus,
                       self.PlasticStrain,
                       self.ExpansionCoef,
                       self.RefTemp, 
                       self.Conductivity,
                       self.SpecificHeat]
        if self.AnalisysType.getActiveEnum() == AnalisysType.Hyperelastic:
            enabled = [self.AnalisysType,
                       #self.HardeningType,
                       #self.ExpansionType,
                       self.HyperelasticType,
                       self.Desnsity,
                       #self.YoungModulus,
                       self.PlasticStrain,
                       self.ExpansionCoef,
                       self.RefTemp,
                       self.Conductivity,
                       self.SpecificHeat]

        disabled: set[TextDialogElement | ComboDialogElement] = set(self.elementList) - set(enabled)
        [i.widget.setEnabled(True) for i in enabled]
        [i.widget.setEnabled(False) for i in disabled]

        match self.AnalisysType.getActiveEnum():
            case AnalisysType.Elastic | AnalisysType.ElastoPlastic:
                if self.AnalisysType.getActiveEnum() == AnalisysType.ElastoPlastic:
                    self.PlasticStrain.widget.setPlaceholderText('σVM, εeq, <temp>')
                    self.PlasticStrain.widget.update()
                match self.ExpansionType.getActiveEnum():
                    case ExpansionType.Iso:
                        self.YoungModulus.widget.setPlaceholderText('Y, ν, <temp>')
                        self.YoungModulus.widget.update()
                    case ExpansionType.Ortho:
                        self.YoungModulus.widget.setPlaceholderText('D1111, D1122, D2222, D1133, D2233, D3333, D1212, D1313\nD2323, <temp>')
                        self.YoungModulus.widget.update()
                    case ExpansionType.Aniso:
                        self.YoungModulus.widget.setPlaceholderText('D1111, D1122, D2222, D1133, D2233, D3333, D1112, D2212\nD3312, D1212, D1113, D2213, D3313, D1213, D1313, D1123\nD2223, D3323, D1223, D1323, D2323, <temp>')
                        self.YoungModulus.widget.update()
            case AnalisysType.Hyperelastic:
                match self.HyperelasticType.getActiveEnum():
                    case HyperelasticType.ArrudaBoyce:
                        self.PlasticStrain.widget.setPlaceholderText('μ, λm, D, <temp>')
                        self.PlasticStrain.widget.update()
                    case HyperelasticType.MooneyRivlin:
                        self.PlasticStrain.widget.setPlaceholderText('C10, C01, D1, <temp>')
                        self.PlasticStrain.widget.update()
                    case HyperelasticType.NeoHooke:
                        self.PlasticStrain.widget.setPlaceholderText('C10, D1, <temp>')
                        self.PlasticStrain.widget.update()
                    case HyperelasticType.Ogden:
                        self.PlasticStrain.widget.setPlaceholderText('μ1, α1, D1, <temp>')
                        self.PlasticStrain.widget.update()
                        #TODO add odgen n=2 and so on
                    case HyperelasticType.Polynomial:
                        self.PlasticStrain.widget.setPlaceholderText('C10, C01, D1, <temp>')
                        self.PlasticStrain.widget.update()
                    case HyperelasticType.ReducedPolynomial:
                        self.PlasticStrain.widget.setPlaceholderText('C10, D1, <temp>')
                        self.PlasticStrain.widget.update()
                    case HyperelasticType.Yeoh:
                        self.PlasticStrain.widget.setPlaceholderText('C10, C20, C30, D1, D2, D3, <temp>')
                        self.PlasticStrain.widget.update()
                    case HyperelasticType.Hyperfoam:
                        self.PlasticStrain.widget.setPlaceholderText('μ1, α1, ν1, <temp>')
                        self.PlasticStrain.widget.update()

    def save_text(self):
        textArr: list = []
        match self.AnalisysType.getValue():
            case AnalisysType.Elastic:
                textArr.append(f'*MATERIAL, NAME={self.writer.text()}\n')
                textArr.append(f'*DENSITY\n')
                textArr.append(f'{self.Desnsity.getValue()}\n')
                textArr.append(f'{self.AnalisysType.getValue()}')
                textArr.append(f', TYPE={self.ExpansionType.getValue()}\n')
                textArr.append(f'{self.YoungModulus.getValue()}\n')
                textArr.append(f'*EXPANSION, ZERO={self.RefTemp.getValue()}\n')
                textArr.append(f'{self.ExpansionCoef.getValue()}\n')
                textArr.append(f'*CONDUCTIVITY\n')
                textArr.append(f'{self.Conductivity.getValue()}\n')
                textArr.append(f'*SPECIFIC HEAT\n')
                textArr.append(f'{self.SpecificHeat.getValue()}\n')
            case AnalisysType.ElastoPlastic:
                textArr.append(f'*MATERIAL, NAME={self.writer.text()}\n')
                textArr.append(f'*DENSITY\n')
                textArr.append(f'{self.Desnsity.getValue()}\n')
                textArr.append(f'*ELASTIC')
                textArr.append(f', TYPE={self.ExpansionType.getValue()}\n')
                textArr.append(f'{self.YoungModulus.getValue()}\n')
                textArr.append(f'{self.AnalisysType.getValue()}')
                textArr.append(f', HARDENING={self.HardeningType.getValue()}\n')
                textArr.append(f'{self.PlasticStrain.getValue()}\n')
                textArr.append(f'*EXPANSION, ZERO={self.RefTemp.getValue()}\n')
                textArr.append(f'{self.ExpansionCoef.getValue()}\n')
                textArr.append(f'*CONDUCTIVITY\n')
                textArr.append(f'{self.Conductivity.getValue()}\n')
                textArr.append(f'*SPECIFIC HEAT\n')
                textArr.append(f'{self.SpecificHeat.getValue()}\n')
            case AnalisysType.Hyperelastic:
                textArr.append(f'*MATERIAL, NAME={self.writer.text()}\n')
                textArr.append(f'*DENSITY\n')
                textArr.append(f'{self.Desnsity.getValue()}\n')
                textArr.append(f'{self.AnalisysType.getValue()}')
                textArr.append(f', {self.HyperelasticType.getValue()}\n')
                textArr.append(f'{self.PlasticStrain.getValue()}\n')
                textArr.append(f'*EXPANSION, ZERO={self.RefTemp.getValue()}\n')
                textArr.append(f'{self.ExpansionCoef.getValue()}\n')
                textArr.append(f'*CONDUCTIVITY\n')
                textArr.append(f'{self.Conductivity.getValue()}\n')
                textArr.append(f'*SPECIFIC HEAT\n')
                textArr.append(f'{self.SpecificHeat.getValue()}\n')

        self.writer.setStoredText(listToText(textArr))
        print(listToText(textArr))

    def loadDialogFromText(self) -> None:
        stream: str = self.writer.getStoredText()
        #TODO implement loading dialog from ccx text 

### Section dialog
class CCXWriterCategory(Enum):
    MeshSubWriter = auto()
    MaterialSubWriter = auto()
    SectionSubWriter = auto()
    ConstraintSubWriter = auto()
    ContactSubWriter = auto()
    AmplitudeSubWriter = auto()
    InitialConditionSubWriter = auto()
    StepSubWriter = auto()
    BoundarySubWriter = auto()
    AnalysisSubWriter = auto()

def CreateDynamicComboBox(items: list[str]):
    tmpComboBox:QComboBox = QComboBox()
    for i in items:
        tmpComboBox.addItem(i)
    return tmpComboBox

class ComboDynamicElement:
    def __init__(self, label: str, comboboxList: list, elemntsList: list):
        self.label: QLabel = QLabel(label)
        self.elemntEnum = comboboxList
        self.widget: QComboBox = CreateDynamicComboBox(comboboxList)
        elemntsList.append(self)

    def getValue(self) -> str:
        return self.widget.currentText()

    def getActiveEnum(self) -> str:
        return self.widget.currentText()

    def setValue(self, val: StrEnum):
        self.widget.setCurrentText(val.name)

class SectionDialog(QDialog):
    def __init__(self, writer: 'CcxWriter'):
        self.elementList: list[ComboDynamicElement] = []

        self.SelectionSet = ComboDynamicElement('Selection set:', [], self.elementList)
        self.Material = ComboDynamicElement('Material:', [], self.elementList)

        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)

        self.llayout = QGridLayout(self)
        for i, elemnt in enumerate(self.elementList):
            self.llayout.addWidget(elemnt.label, i, 0)
            self.llayout.addWidget(elemnt.widget, i, 1)

        self.ok_button = QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.save_text)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)

        lastRow:int = self.llayout.rowCount()
        self.llayout.addWidget(self.cancel_button, lastRow, 0)
        self.llayout.addWidget(self.ok_button, lastRow, 1)

        self.updateFields()

    def setupTestvalues(self):
        pass

    def updateFields(self):
        materials = self.writer.getWritersListByCategory(CCXWriterCategory.MaterialSubWriter)
        self.materialsList = [i.text() for i in materials]
        self.Material.widget.clear()
        self.Material.widget.addItems(self.materialsList)

    def save_text(self):
        textArr: list = []
        textArr.append(f'{self.SpecificHeat.getValue()}\n')

        self.writer.setStoredText(listToText(textArr))
        print(listToText(textArr))

    def loadDialogFromText(self) -> None:
        stream: str = self.writer.getStoredText()
        #TODO implement loading dialog from ccx text 

### Raw text editor
class TextEditor(QDialog):
    def __init__(self, writer: 'CcxWriter'):
        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)

        self.llayout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.llayout.addWidget(self.text_edit)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_text)
        self.llayout.addWidget(self.save_button)

    def save_text(self):
        text = self.text_edit.toPlainText()
        self.writer.setStoredText(text)

    def exec(self) -> int:
        self.text_edit.setPlainText(self.writer.getStoredText())
        return super().exec()


if __name__ == "__main__":
    print(get_option_from_json("options.json", "ccx_path"))
