# SET FIELDS FOR WIZARD
# df = df
# filePath = path to df
# maxTests = max tests per day
# maxDays = max days of finals (can be exceeded)

import numpy as np
import pandas as pd
import regex as re
from pathlib import Path
from PyQt6.QtWidgets import QPushButton, QFileDialog, QLineEdit, QFormLayout, QWidget, QGridLayout, QScrollArea

from old_code import generationStart
from QtObjects.WizardPage import WizardPage
from QtObjects.WrappedLabel import WrappedLabel

def introPage(page: WizardPage):        
    page.widgets.append(WrappedLabel('Welcome to the Simmons University Finals Exam Schedule Wizard. '
                   'This wizard will walk you through the step needed '
                   'to customize and create this semester\'s exam schedule.<br><br>'
                   'To proceed to the next page, select the \'Next\' button on the bottom right.'
                   '<br><br>Add a help button here probably'))

def importSpreadsheet(page: WizardPage):
    def getCourses(df: pd.DataFrame):
        """Get courses by dropping unneeded columns, removing labs and SIM classes, and sorting values"""
        
        df = df.dropna()
        df = df[['CourseSection']]
        # Labs match the below pattern with a Course code, 3 numbers, and an L
        pattern = r'\w+ \d+L-.*'
        df = df[~df['CourseSection'].str.contains(pattern)]
        df = df[~df['CourseSection'].str.contains('SIM')]
        df = df[~df['CourseSection'].str.contains('CR')]
        # Remove course sections from string
        df['CourseSection'] = df['CourseSection'].str.replace(r'-\w*', '', regex=True)
        return df.drop_duplicates().sort_values(by=['CourseSection'])

    def readCSV(csv):
        df = getCourses(pd.read_csv(csv, index_col=False))
        # Save df and filepath to page.wizard() for future access
        page.wizard().df = df
        page.wizard().filePath = csv

    def openFileDialog():
        filename = QFileDialog.getOpenFileName(page, 'CSV (*.csv);;Excel (*.xlsx)', '/home/leek/Coding')
        # If selected file exists, try to parse data
        if filename[0]:
            path = Path(filename[0])
            try:
                readCSV(path)
                page.fileNameText.setText(str(path))
            except:
                # For debugging
                print(f'Bad File: {path} is not a valid file type')
                page.showErrorPage(f'{path} is <b>not a valid file type</b>. Please select a <b>CSV file</b>')

    page.widgets.append(WrappedLabel('Select a CSV file containing student course enrollment information. '
                   'This file will be used to generate the finals schedule, so make sure it is up-to-date.'))
    
    # File selection button
    fileBrowser = QPushButton('Browse Files')
    fileBrowser.clicked.connect(openFileDialog)
    page.widgets.append(fileBrowser)

    # Set read only so user must click on button
    page.fileNameText = QLineEdit('No file selected')
    page.fileNameText.setReadOnly(True)
    page.widgets.append(page.fileNameText)

    # Register filePath field when updated
    page.registerField('filePath*', page.fileNameText, 'text', page.fileNameText.textChanged)

def selectCourses(page: WizardPage):
    def getMajor(course: str):
        pattern = r'(\w*) \d{3}'
        return re.search(pattern, course)[1]

    def toggleCourses(course: str):
        def f():
            page.wizard().courses[course] = not page.wizard().courses[course]
            # Debugging
            print(f'Course Status Change: {course} = {page.wizard().courses[course]}')
        return f
    
    page.widgets.append(WrappedLabel('Below is a list of all the classes given this semester. '
    'Please which classes are and arent giving finals by toggling the button for each course.'))

    page.wizard().courses = {}
    row = 0
    column = 0

    layout = QScrollArea()
    mainWidget = QWidget()
    grid = QGridLayout()

    previousMajor = getMajor(page.wizard().df['CourseSection'][1])
    for i in page.wizard().df['CourseSection']:
        page.wizard().courses[i] = False
        button = QPushButton(i)
        button.setCheckable(True)
        currentMajor = getMajor(i)
        if column == 4 and currentMajor == previousMajor:
            column = 0
            row += 1
        elif currentMajor == previousMajor:
            column += 1
        else:
            column = 0
            row += 1
            previousMajor = currentMajor
        button.toggled.connect(toggleCourses(button.text()))
        grid.addWidget(button, row, column)
        
    mainWidget.setLayout(grid)
    layout.setWidget(mainWidget)
    page.widgets.append(layout)
        

def customizeDetails(page: WizardPage):
    def updateMaxVariables():
        page.wizard().maxTests = maxTestsEdit.text()
        page.wizard().maxDays = maxDaysEdit.text()
    label = WrappedLabel('Customize the schedule details here by changing the maximum number of tests per a day '
                   'and the maximum number of days for exams. '
                   '(The maximum number of days may be exceeded because of student scheduling conflicts '
                   'but a warning will be produced explaining the issue)')
    page.widgets.append(label)

    innerLayout = QFormLayout()
    maxTestsEdit = QLineEdit('4')
    maxDaysEdit = QLineEdit('4')

    innerLayout.addRow('Max Daily Finals:', maxTestsEdit)
    innerLayout.addRow('Max Final Days:', maxDaysEdit)

    maxTestsEdit.textChanged.connect(updateMaxVariables)
    maxDaysEdit.textChanged.connect(updateMaxVariables)
    # Register maxTests and maxDays fields when updated
    page.registerField('maxTests', maxTestsEdit, 'text', maxTestsEdit.textChanged)
    page.registerField('maxDays', maxDaysEdit, 'text', maxDaysEdit.textChanged)

    page.wizard().maxTests = maxTestsEdit.text()
    page.wizard().maxDays = maxDaysEdit.text()
    page.layout.addLayout(innerLayout)

def reviewInfo(page: WizardPage):
    def getFinals():
        return [key for key, _ in page.wizard().courses.items() if page.wizard().courses[key]]

    label = WrappedLabel('Confirm the following configuration.')
    page.widgets.append(label)

    layout = QFormLayout()
    layout.addRow('Spreadsheet Location:', WrappedLabel(str(page.wizard().filePath)))
    layout.addRow('Courses With Finals:', WrappedLabel(', '.join(getFinals())))
    layout.addRow('Max Daily Finals:', WrappedLabel(page.wizard().field('maxTests')))
    layout.addRow('Max Final Days:', WrappedLabel(page.wizard().field('maxDays')))
    
    page.layout.addLayout(layout)

def generateSchedule(page: WizardPage):
    path = page.wizard().filePath
    courses = page.wizard().courses
    maxTests = page.wizard().maxTests
    maxDays = page.wizard().maxDays
    generationStart(path, courses, maxTests, maxDays)