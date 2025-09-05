import sys
from PyQt6.QtWidgets import QApplication, QWizard

from QtObjects.WizardPage import WizardPage
from subpageContents import (
    introPage, importSpreadsheet, selectCourses,
    customizeDetails, reviewInfo, generateSchedule
)

# KEY: Index (int)
# VALUE: ['Page Title', Page Create Function, Reset Page Layout When Backtracking]
WIZARD_PAGES = {0: ['Introduction', introPage, False],
                1: ['Import Spreadsheet', importSpreadsheet, False],
                2: ['Select Courses', selectCourses, True],
                3: ['Customize Details', customizeDetails, False],
                4: ['Review Information', reviewInfo, True],
                5: ['Generate Schedule', generateSchedule, False]}

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create QWizard instance
    wizard = QWizard()
    wizard.setWindowTitle('Simmons University Finals Exam Schedule Wizard')
    wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
    wizard.resize(app.primaryScreen().size() / 2.5)

    # Make list of all page titles
    pageTitles = [WIZARD_PAGES[key][0] for key in sorted(WIZARD_PAGES)]

    for key in sorted(WIZARD_PAGES.keys()):
        func = WIZARD_PAGES[key][1]
        resetPage = WIZARD_PAGES[key][2]
        wizard.addPage(WizardPage(pageTitles, key, func, resetPage))

    # Show the wizard and run event loop
    wizard.show()
    sys.exit(app.exec())
