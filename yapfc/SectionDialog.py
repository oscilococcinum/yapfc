from PySide6.QtWidgets import (
    QDialog, QComboBox, QPushButton,
    QDialog, QLabel, QPushButton,
    QLabel, QGridLayout, QComboBox
)
from enum import StrEnum
from typing import TYPE_CHECKING
from yapfc.CCXWriterCategory import CCXWriterCategory

if TYPE_CHECKING:
    from yapfc.model import CcxWriter

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
        super().__init__()
        self.writer = writer
        self.setWindowTitle(writer.text())
        self.setGeometry(100, 100, 400, 300)
        self.llayout = QGridLayout(self)
        self.elementList: list[ComboDynamicElement] = []

        self.SelectionSet = ComboDynamicElement('Selection set:', [], self.elementList)
        self.Material = ComboDynamicElement('Material:', [], self.elementList)

        self.SetupGui(self.llayout, self.elementList)
        self.updateFields()

    def setupTestvalues(self):
        pass

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
        materials = self.writer.getWritersListByCategory(CCXWriterCategory.MaterialSubWriter)
        self.materialsList = [i.text() for i in materials]
        self.Material.widget.clear()
        self.Material.widget.addItems(self.materialsList)

    def save_text(self):
        #textArr: list = []
        #textArr.append(f'{self.SpecificHeat.getValue()}\n')

        #self.writer.setStoredText(listToText(textArr))
        #print(listToText(textArr))
        pass

    def loadDialogFromText(self) -> None:
        stream: str = self.writer.getStoredText()
        #TODO implement loading dialog from ccx text 