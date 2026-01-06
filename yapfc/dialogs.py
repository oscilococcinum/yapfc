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

class TextDialogElement:
    def __init__(self, label: str, elemntsList: list):
        self.label: QLabel = QLabel(label)
        self.widget: QPlainTextEdit = QPlainTextEdit()
        elemntsList.append(self)

    def getValue(self) -> str:
        return self.widget.toPlainText()

class MaterialDialog(QDialog):
    def __init__(self, writer: 'CcxWriter'):
        elementList: list[ComboDialogElement | TextDialogElement] = []
        self.AnalisysType = ComboDialogElement('Type', AnalisysType, elementList)
        self.HardeningType = ComboDialogElement('Hardening', HardeningType, elementList)
        self.HyperelasticType = ComboDialogElement('Hyperelastic Model', HyperelasticType, elementList)
        self.Desnsity = TextDialogElement('Density', elementList)
        self.YoungModulus = TextDialogElement('Young Modulus', elementList)
        self.PlasticStrain = TextDialogElement('Plastic Strain', elementList)
        self.ExpansionCoef = TextDialogElement('Expansion Coef.', elementList)
        self.RefTemp = TextDialogElement('Ref. Temp.', elementList)
        self.ExpansionType = TextDialogElement('Expansion Type', elementList)
        self.Conductivity = TextDialogElement('Conductivity', elementList)
        self.SpecificHeat = TextDialogElement('Specific Heat', elementList)

        self.HardeningType.widget.setEnabled(False)
        self.HyperelasticType.widget.setEnabled(False)

        self.AnalisysType.widget.currentTextChanged.connect(self.updateFields)
        self.HardeningType.widget.currentTextChanged.connect(self.updateFields)
        self.HyperelasticType.widget.currentTextChanged.connect(self.updateFields)
        # TODO add rest

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

    def updateFields(self):
        if self.AnalisysType.elemntEnum[self.AnalisysType.widget.currentText()] == AnalisysType.ElastoPlastic:
            self.HardeningType.widget.setEnabled(True)
        else:
            self.HardeningType.widget.setEnabled(False)
        if self.AnalisysType.elemntEnum[self.AnalisysType.widget.currentText()] == AnalisysType.Hyperelastic:
            self.HyperelasticType.widget.setEnabled(True)
        else:
            self.HyperelasticType.widget.setEnabled(False)

    def save_text(self):
        textArr: list = []
        match self.AnalisysType.getValue():
            case AnalisysType.Elastic:
                textArr.append(f'*MATERIAL, NAME={self.writer.getTextLabel()}\n')
                textArr.append(f'{self.AnalisysType.getValue()}')
                textArr.append(f', TYPE={self.HardeningType.getValue()}\n')
                textArr.append(f'{self.YoungModulus.getValue()}\n')
                textArr.append(f'*DENSITY\n')
                textArr.append(f'{self.Desnsity.getValue()}\n')
            case AnalisysType.ElastoPlastic:
                textArr.append(f'*MATERIAL, NAME={self.writer.getTextLabel()}\n')
                textArr.append(f'*ELASTIC\n')
                textArr.append(f'{self.YoungModulus.getValue()}\n')
                textArr.append(f'{self.AnalisysType.getValue()}')
                textArr.append(f', TYPE={self.HardeningType.getValue()}\n')
                textArr.append(f'{self.PlasticStrain.getValue()}\n')
                textArr.append(f'*DENSITY\n')
                textArr.append(f'{self.Desnsity.getValue()}\n')
            case AnalisysType.Hyperelastic:
                textArr.append(f'*MATERIAL, NAME={self.writer.getTextLabel()}\n')
                textArr.append(f'{self.AnalisysType.getValue()}')
                textArr.append(f', {self.HyperelasticType.getValue()}\n')
                textArr.append(f'{self.PlasticStrain.getValue()}\n')
                textArr.append(f'*DENSITY\n')
                textArr.append(f'{self.Desnsity.getValue()}\n')


        self.writer.setStoredText(listToText(textArr))
        print(listToText(textArr))

### Raw text editor

class TextEditor(QDialog):
    def __init__(self, writer: 'CcxWriter'):
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


if __name__ == "__main__":
    print(get_option_from_json("options.json", "ccx_path"))
