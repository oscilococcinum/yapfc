from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QDialog, QComboBox, QPushButton, QLabel, QGridLayout, QComboBox,
    QDialog, QLabel, QPushButton, QPlainTextEdit
)
from yapfc.enums.AnalisysType import AnalisysType
from yapfc.enums.ExpansionType import ExpansionType
from yapfc.enums.HardeningType import HardeningType
from yapfc.enums.HyperelasticType import HyperelasticType
from enum import StrEnum
from yapfc.util import listToText
if TYPE_CHECKING:
    from yapfc.model import CcxWriter


def CreateComboBox(items: type[StrEnum]):
    tmpComboBox:QComboBox = QComboBox()
    for i in items:
        tmpComboBox.addItem(i.name)
    return tmpComboBox

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
        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)
        self.llayout = QGridLayout(self)
        self.elementList: list[ComboDialogElement | TextDialogElement] = []

        self.AnalisysType = ComboDialogElement('Type', AnalisysType, self.elementList)
        self.HardeningType = ComboDialogElement('Hardening', HardeningType, self.elementList)
        self.ExpansionType = ComboDialogElement('Elastic Expansion Type', ExpansionType, self.elementList)
        self.HyperelasticType = ComboDialogElement('Hyperelastic Model', HyperelasticType, self.elementList)
        self.Desnsity = TextDialogElement('Density', self.elementList)
        self.YoungModulus = TextDialogElement('Young Modulus\nOrtho, Aniso Coef.', self.elementList)
        self.PlasticStrain = TextDialogElement('Plastic Strain\nHyperelastic Coef.', self.elementList)
        self.ExpansionCoef = TextDialogElement('Expansion Coef.', self.elementList)
        self.RefTemp = TextDialogElement('Ref. Temp.', self.elementList)
        self.Conductivity = TextDialogElement('Conductivity', self.elementList)
        self.SpecificHeat = TextDialogElement('Specific Heat', self.elementList)

        self.HardeningType.widget.setEnabled(False)
        self.HyperelasticType.widget.setEnabled(False)

        self.AnalisysType.widget.currentTextChanged.connect(self.updateFields)
        self.HardeningType.widget.currentTextChanged.connect(self.updateFields)
        self.HyperelasticType.widget.currentTextChanged.connect(self.updateFields)
        self.ExpansionType.widget.currentTextChanged.connect(self.updateFields)

        self.SetupGui(self.llayout, self.elementList)
        self.updateFields()
        self.setupTestvalues()

    def setupTestvalues(self):
        [i.setValue(j) for i,j  in zip(self.elementList,[AnalisysType.ElastoPlastic, #type: ignore
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

    def SetupGui(self, llayout, elementList: list) -> None:
        for i, elemnt in enumerate(elementList):
            self.llayout.addWidget(elemnt.label, i, 0)
            self.llayout.addWidget(elemnt.widget, i, 1)

        self.ok_button = QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.save_text)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)

        lastRow:int = self.llayout.rowCount()
        llayout.addWidget(self.cancel_button, lastRow, 0)
        llayout.addWidget(self.ok_button, lastRow, 1)

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