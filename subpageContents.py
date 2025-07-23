# TO DO: REMOVE label.setWordWrap(True)

# SET FIELDS FOR WIZARD
# filePath = path to df
# maxTests = max tests per day
# maxDays = max days of finals (can be exceeded)

from pathlib import Path
from PyQt6.QtWidgets import QLabel, QPushButton, QFileDialog, QLineEdit, QFormLayout, QWizard

from WizardPage import WizardPage

def addWidgets(page: WizardPage, list: list):
    for widget in list:
        page.layout.addWidget(widget)
    return page

def introPage(page: WizardPage):        
    label = QLabel("Welcome to the Simmons University Finals Exam Schedule Wizard. "
                   "This wizard will walk you through the step needed"
                   "to customize and create this semester's exam schedule.<br><br>"
                   "To proceed to the next page, select the \"Next\" button on the bottom right."
                   "<br><br>Add a help button here probably")
    label.setWordWrap(True)

    page = addWidgets(page, [label])

def importSpreadsheet(page: WizardPage):
    def openFileDialog():
        filename = QFileDialog.getOpenFileName(page, "Select a File", "/home/leek/Coding", "Python files (*.py)")
        if filename[0]:
            path = Path(filename[0])
            page.fileNameText.setText(str(path))

    widgets = []

    label = QLabel("Select a CSV file containing student course enrollment information."
                   "This file will be used to generate the finals schedule, so make sure it is up-to-date.")
    label.setWordWrap(True)
    widgets.append(label)
    
    # File selection button
    fileBrowser = QPushButton("Browse Files")
    fileBrowser.clicked.connect(openFileDialog)
    widgets.append(fileBrowser)

    # Set read only so user must click on button
    page.fileNameText = QLineEdit("No file selected")
    page.fileNameText.setReadOnly(True)
    widgets.append(page.fileNameText)

    # Register filePath field when updated
    page.registerField("filePath*", page.fileNameText, "text", page.fileNameText.textChanged)
    page = addWidgets(page, widgets)

def selectCourses(page: WizardPage, wizard: QWizard):
    pass

def customizeDetails(page: WizardPage):
    widgets = []

    label = QLabel("Customize the schedule details here by changing the maximum number of tests per a day"
                   "and the maximum number of days for exams. "
                   "(The maximum number of days may be exceeded because of student scheduling conflicts "
                   "but a warning will be produced explaining the issue)")
    label.setWordWrap(True)
    widgets.append(label)

    innerLayout = QFormLayout()
    maxTestsEdit = QLineEdit("4")
    maxDaysEdit = QLineEdit("4")

    innerLayout.addRow('Max Daily Finals:', maxTestsEdit)
    innerLayout.addRow('Max Final Days:', maxDaysEdit)

    # Register maxTests and maxDays fields when updated
    page.registerField("maxTests", maxTestsEdit, "text", maxTestsEdit.textChanged)
    page.registerField("maxDays", maxDaysEdit, "text", maxDaysEdit.textChanged)

    page = addWidgets(page, widgets)
    page.layout.addLayout(innerLayout)

def reviewInfo(page: WizardPage, wizard: QWizard):
    pass
