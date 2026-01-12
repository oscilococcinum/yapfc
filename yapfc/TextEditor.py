import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton,
    QVBoxLayout, QDialog, QPushButton, QTextEdit
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from yapfc.model import CcxWriter


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