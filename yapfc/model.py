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


class Writer(QStandardItem):
    def __init__(self, text="Writer"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = ""

    def doubleClicked(self):
        self.editor = TextEditor(self)
        self.editor.exec()

    def set_text(self, text):
        self.stored_text = text

    def get_text(self):
        return self.stored_text


class Step(Writer):
    def __init__(self, text="Step"):
        super().__init__(text)
        self.setEditable(False)
        self.stored_text = "*Step\n*Static, Solver=PaStiX"