from PyQt6.QtWidgets import QWizardPage, QListWidget, QHBoxLayout, QVBoxLayout, QAbstractItemView, QAbstractItemView

class WizardPage(QWizardPage):
    """Class for formatted pages in QWizard application"""
    def __init__(self, wizardPages: list[str], currentIndex: int, updateLayout: callable, wizard: QWizardPage=None) -> None:
        super().__init__()
        self.setTitle(wizardPages[currentIndex])

        # Wizard page directory. Adds all pages to list and highlights current paage
        self.listView = QListWidget()
        self.listView.addItems(wizardPages)
        self.listView.setCurrentRow(currentIndex)
        # Prevents other items from being highlighted
        self.listView.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        # Set list width to minimum possible size + padding
        self.listView.setFixedWidth(self.listView.sizeHintForColumn(0) + 10)

        # HBox contains page list on left, additional info on right
        parentLayout = QHBoxLayout()
        parentLayout.addWidget(self.listView)
        # self.layout can be edited to contain page specific info
        self.layout = QVBoxLayout()

        # Combine layouts and add to parent
        parentLayout.addLayout(self.layout)
        self.setLayout(parentLayout)
        
        if wizard == None:
            updateLayout(self)
        else:
            # Pass in wizard as additional param if required by function
            updateLayout(self, wizard)