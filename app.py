from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from click import option
from helper_gui import Ui_MainWindow
import sys

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        # * Input Variables
        # TODO initialize variables here
        self.dataPath = None
        self.gtfPath = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # * Buttons
        self.ui.dataBrowse_button.clicked.connect(self.on_push_dataBrowse)
        self.ui.gtfBrowse_button.clicked.connect(self.on_push_gtfBrowse)

    def on_push_dataBrowse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        # This might be useful for debugging, maybe cross platform? Need to test whether this is necessary
        # options |= QFileDialog.DontUseNativeDialog

        self.dataPath = QFileDialog.getExistingDirectory(
            self, # this refers to a subclass of QWidget
            "Select RNA Data Folder",
            "",
            options = options
        )
        
        if self.dataPath:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Path to RNA Data Set!\n" +
                "Set to: ..." +
                self.dataPath +
                "\n"
            )
            self.ui.data_lineedit.insert(self.dataPath)

    def on_push_gtfBrowse(self):
        options = QFileDialog.Options()

        self.gtfPath, _ = QFileDialog.getOpenFileName(
            self,
            "Select GTF File",
            "",
            "Gene Transfer Format (*.gtf)",
            options = options
        )
        
        if self.gtfPath:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Path to GTF Set!\n" +
                "Set to: ..." +
                self.gtfPath +
                "\n"
            )
            self.ui.gtf_lineedit.insert(self.gtfPath)

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    # ? Order of things to do
    # TODO Get buttons to browse file system
    # TODO Implement option saving with save button, possibly without
    # TODO Print everything from console to the output box
    # TODO Add function to the run button