from PyQt6.QtWidgets import QLabel

class WrappedLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setWordWrap(True)