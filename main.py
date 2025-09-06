import sys
from PyQt6.QtWidgets import QApplication, QWizard

from QtObjects.WizardPageChildren import Introduction, ImportSchedule, SelectCourses, CustomizeDetails, ReviewInfo, GenerateSchedule

WIZARD_PAGES = [['Introduction', Introduction],
                ['Import Spreadsheet', ImportSchedule],
                ['Select Courses', SelectCourses],
                ['Customize Details', CustomizeDetails],
                ['Review Information', ReviewInfo],
                ['Generate Schedule', GenerateSchedule]]

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create QWizard instance
    wizard = QWizard()
    wizard.setWindowTitle('Simmons University Finals Exam Schedule Wizard')
    wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
    wizard.resize(app.primaryScreen().size() / 2.25)

    # Make list of all page titles
    pageTitles = [page[0] for page in WIZARD_PAGES]

    for index in range(len(WIZARD_PAGES)):
        wizardPage = WIZARD_PAGES[index][1]
        wizard.addPage(wizardPage(pageTitles, index))

    # Show the wizard and run event loop
    wizard.show()
    sys.exit(app.exec())