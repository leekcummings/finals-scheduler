import sys
import inspect
from PyQt6.QtWidgets import QApplication, QWizard

from WizardPage import WizardPage
from subpageContents import introPage, importSpreadsheet, selectCourses, customizeDetails, reviewInfo

# KEY: Index (int)
# VALUE: ["Page Title", Page Create Function]
WIZARD_PAGES = {0: ["Introduction", introPage],
                1: ["Import Spreadsheet", importSpreadsheet],
                2: ["Select Courses", selectCourses],
                3: ["Customize Details", customizeDetails],
                4: ["Review Information", reviewInfo]}

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create a QWizard instance
    wizard = QWizard()
    wizard.setWindowTitle(__name__)
    wizard.setWizardStyle(QWizard.WizardStyle.ClassicStyle)

    pageTitles = [WIZARD_PAGES[key][0] for key in sorted(WIZARD_PAGES)]

    for key in sorted(WIZARD_PAGES.keys()):
        page = None
        func = WIZARD_PAGES[key][1]
        # Checks the function passed in to see if it requires the wizard parameter
        for i in inspect.signature(func).parameters.values():
            if i.annotation == QWizard:
                page = WizardPage(pageTitles, key, func, wizard)
        if not page:
            page = WizardPage(pageTitles, key, func)

        wizard.addPage(page)

    # Show the wizard and run event loop
    wizard.show()
    sys.exit(app.exec())