import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QRadioButton,
    QComboBox, QPushButton, QLabel, QLineEdit
)

def get_option_from_json(json_file:str, option:str) -> str:
        try:
            with open(f"{json_file}", "r") as f:
                options = json.load(f)
                return options.get(f"{option}", "")
        except FileNotFoundError:
            pass

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


if __name__ == "__main__":
    print(get_option_from_json("options.json", "ccx_path"))