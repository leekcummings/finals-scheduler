import json
import numpy as np
import pandas as pd
from pathlib import Path
import regex as re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QPushButton, QLineEdit, QScrollArea, QWidget, QGridLayout, QFormLayout

from QtObjects.WizardPage import WizardPage, WrappedLabel
from old_code import generationStart

# Page 1: Introduction
class Introduction(WizardPage):
    def __init__(self, wizardPages, currentIndex):
        super().__init__(wizardPages, currentIndex)
        label = WrappedLabel('Welcome to the Simmons University Finals Exam Schedule Wizard. '
                   'This wizard will walk you through the step needed '
                   'to customize and create this semester\'s exam schedule.<br><br>'
                   'To proceed to the next page, select the \'Next\' button on the bottom right.')
        self.layout.addWidget(label)

# Page 2: Import CSV with student course information
class ImportSchedule(WizardPage):
    def __init__(self, wizardPages, currentIndex):
        super().__init__(wizardPages, currentIndex)
        label = WrappedLabel('Select a CSV file containing student course enrollment information. '
                   'This file will be used to generate the finals schedule, so make sure it is up-to-date.')
        self.layout.addWidget(label)

        # File selection button
        fileBrowser = QPushButton('Browse Files')
        fileBrowser.clicked.connect(self.openFileDialog)
        self.layout.addWidget(fileBrowser)

        # Set read only so user must click on button
        self.fileNameText = QLineEdit('No file selected')
        self.fileNameText.setReadOnly(True)
        self.layout.addWidget(self.fileNameText)

        # Register filePath field when updated
        self.registerField('filePath*', self.fileNameText, 'text', self.fileNameText.textChanged)

    def getCourses(self, df: pd.DataFrame):
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

    def readCSV(self, csv):
        df = self.getCourses(pd.read_csv(csv, index_col=False))
        # Save df and filepath to self.wizard() for future access
        self.wizard().df = df
        self.wizard().filePath = csv
        # Debugging
        print(f'File Path Change: {csv}')

    def openFileDialog(self):
        downloads = str(Path.home() / "Downloads")
        filename = QFileDialog.getOpenFileName(self, 'CSV Files (*.csv)', downloads)
        # If selected file exists, try to parse data
        if filename[0]:
            path = Path(filename[0])
            try:
                self.readCSV(path)
                self.fileNameText.setText(str(path))
            except:
                # For debugging
                print(f'Bad File: {path} is not a valid file type')
                self.showErrorPage(f'{path} is <b>not a valid file type</b>. Please select a <b>CSV file</b>')

#  Page 3: Select which courses have finals
class SelectCourses(WizardPage):
    def __init__(self, wizardPages, currentIndex):
        super().__init__(wizardPages, currentIndex)
        # Initialize df to compare
        self.filePath = ''

        with open('courseFinals.json') as f:
                self.courseDefaults = json.load(f)

    def initializePage(self):
        # If there is an updated df, reload the page
        if self.wizard().filePath != self.filePath:
            self.resetLayout(self.layout)
            self.filePath = self.wizard().filePath

            self.layout.addWidget(WrappedLabel('Below is a list of all the classes given this semester. '
            'Please which classes are and arent giving finals by toggling the button for each course.'))

            # Store selected courses in wizard
            self.wizard().courses = {}

            # Count rows and columns to display courses in QWidget
            row = 0
            column = 0
            layout = QScrollArea()
            mainWidget = QWidget()
            grid = QGridLayout()

            previousMajor = self.getMajor(self.wizard().df['CourseSection'][0])

            for i in self.wizard().df['CourseSection']:
                # Create clickable button for each course
                button = QPushButton(i)
                button.setCheckable(True)

                currentMajor = self.getMajor(i)
                # Use preset values to determine if course have finals
                # If no preset, assume no final
                if currentMajor in self.courseDefaults:
                    value = self.courseDefaults[currentMajor]
                    self.wizard().courses[i] = value
                    button.setChecked(value)
                else:
                    self.wizard().courses[i] = False

                # End column before overflow
                if column == 4 and currentMajor == previousMajor:
                    column = 0
                    row += 1
                elif currentMajor == previousMajor:
                    column += 1
                else:
                    column = 0
                    row += 1
                    previousMajor = currentMajor
                # Connect button to allow changing finals status
                button.toggled.connect(self.toggleCourses(button.text()))
                grid.addWidget(button, row, column)
            
            mainWidget.setLayout(grid)
            layout.setWidget(mainWidget)
            self.widgets.append(layout)
            
            # Add widgets to layout
            self.addWidgets(self.widgets)


    def getMajor(self, course: str):
        pattern = r'(\w*) \d{3}'
        return re.search(pattern, course)[1]

    def toggleCourses(self, course: str):
        def f():
            self.wizard().courses[course] = not self.wizard().courses[course]
            # Debugging
            print(f'Course Status Change: {course} = {self.wizard().courses[course]}')
        return f

class CustomizeDetails(WizardPage):
    def __init__(self, wizardPages, currentIndex):
        super().__init__(wizardPages, currentIndex)
        
    def initializePage(self):
        # Using initializePage instead of __init__ to add this
        # Using self.wizard() doesn't work in __init__ because the page hasn't been added to the wizard yet
        if self.layout.isEmpty():
            label = WrappedLabel('Customize the schedule details here by changing the maximum number of tests per a day '
                    'and the maximum number of days for exams. '
                    '(The maximum number of days may be exceeded because of student scheduling conflicts '
                    'but a warning will be produced explaining the issue)')
            self.layout.addWidget(label)

            innerLayout = QFormLayout()
            self.maxTestsEdit = QLineEdit('4')
            self.maxDaysEdit = QLineEdit('4')

            innerLayout.addRow('Max Daily Finals:', self.maxTestsEdit)
            innerLayout.addRow('Max Final Days:', self.maxDaysEdit)

            self.maxTestsEdit.textChanged.connect(self.updateMaxVariables)
            self.maxDaysEdit.textChanged.connect(self.updateMaxVariables)
            # Register maxTests and maxDays fields when updated
            self.registerField('maxTests', self.maxTestsEdit, 'text', self.maxTestsEdit.textChanged)
            self.registerField('maxDays', self.maxDaysEdit, 'text', self.maxDaysEdit.textChanged)

            self.wizard().maxTests = self.maxTestsEdit.text()
            self.wizard().maxDays = self.maxDaysEdit.text()
            self.layout.addLayout(innerLayout)
        
    def updateMaxVariables(self):
        # Update wizard variables if changed
        self.wizard().maxTests = self.maxTestsEdit.text()
        self.wizard().maxDays = self.maxDaysEdit.text()

class ReviewInfo(WizardPage):
    def __init__(self, wizardPages, currentIndex):
        super().__init__(wizardPages, currentIndex)
        self.setCommitPage(True)

    def initializePage(self):
        # Refresh layout every time page opened
        self.resetLayout(self.layout)
        self.layout.addWidget(WrappedLabel('Confirm the following configuration.'))

        layout = QFormLayout()
        layout.addRow('Spreadsheet Location:', WrappedLabel(str(self.wizard().filePath)))
        label = WrappedLabel(', '.join(self.getFinals()))
        layout.addRow('Courses With Finals:', label)
        layout.addRow('Max Daily Finals:', WrappedLabel(self.wizard().field('maxTests')))
        layout.addRow('Max Final Days:', WrappedLabel(self.wizard().field('maxDays')))

        self.layout.addLayout(layout)
        # Stretch layout to prevent text clipping
        self.layout.addStretch()

    def getFinals(self):
        return [key for key, _ in self.wizard().courses.items() if self.wizard().courses[key]]
    
class GenerateSchedule(WizardPage):
    def __init__(self, wizardPages, currentIndex):
        super().__init__(wizardPages, currentIndex)

    def initializePage(self):
        label = WrappedLabel('Your file has been generated and saved to "final_schedule.xlsx" in this folder.')
        self.layout.addWidget(label)

        # Generate schedule properties
        path = self.wizard().filePath
        courses = self.wizard().courses
        maxTests = self.wizard().maxTests
        maxDays = self.wizard().maxDays
        generationStart(path, courses, int(maxTests), int(maxDays))
