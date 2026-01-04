import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QRadioButton,
    QComboBox, QPushButton, QLabel, QLineEdit, QGridLayout, QComboBox,
    QVBoxLayout, QDialog, QLabel, QPushButton, QPlainTextEdit, QTextEdit
)
from yapfc.model import CcxWriter

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
    def __init__(self, writer: CcxWriter):
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
    def __init__(self, writer: CcxWriter):
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
