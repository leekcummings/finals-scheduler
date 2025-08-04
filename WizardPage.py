import inspect
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWizard, QWizardPage, QHBoxLayout, QVBoxLayout, QListWidget, QAbstractItemView, QMessageBox

PADDING = 10

class WizardPage(QWizardPage):
    """Class for formatted pages in QWizard application"""
    
    def __init__(self, wizardPages: list[str], currentIndex: int, updateLayout: callable, resetPage: bool) -> None:
        super().__init__()
        self.setTitle(wizardPages[currentIndex])

        # Blank list for widgets to be added to
        self.widgets = []
        self.updateLayout = updateLayout
        self.resetPage = resetPage

        # Wizard page directory. Adds all pages to list and highlights current paage
        self.listView = QListWidget()
        self.listView.addItems(wizardPages)
        self.listView.setCurrentRow(currentIndex)
        # Prevents other items from being highlighted
        self.listView.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        # Set list width to minimum possible size + padding
        self.listView.setFixedWidth(self.listView.sizeHintForColumn(0) + PADDING)

        # HBox contains page list on left, additional info on right
        self.parentLayout = QHBoxLayout()
        self.parentLayout.addWidget(self.listView)
        # self.layout can be edited to contain page specific info
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.parentLayout.addLayout(self.layout)
        self.setLayout(self.parentLayout)

    # This was causing SO MANY ISSUES
    # Thank you @user3369214 on StackOverflow (https://stackoverflow.com/a/23087057)
    def resetLayout(self, layout):
        """Remove all of the widget safetly from page to refresh data"""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.resetLayout(child.layout())

    def initializePage(self):
        """Add widgets and data to page, runs again every time page is switched to"""
        if self.resetPage:
            self.resetLayout(self.layout)
        if self.resetPage or self.layout.isEmpty():
            self.updateLayout(self)
            self.addWidgets(self.widgets)
            self.layout.addStretch()

    def addWidgets(self, list: list):
        for widget in list:
            self.layout.addWidget(widget)
        self.widgets.clear()
        return self

    def showErrorPage(self, text: str):
        """Creates a pop-up showing a warning icon and message for the user"""

        dialog = QMessageBox()
        dialog.setText(text)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("Error!")
        dialog.exec()