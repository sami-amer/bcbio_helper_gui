from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject
from gui_doctor import Ui_MainWindow
import sys
class Stream(QtCore.QObject):
    # * Stream object for console output text
    newText = QtCore.pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))
    
    def flush(self):
        # ? Flush must be implemented, but it can be a no-op
        pass
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        # * Process and Signals for Run
        self.process_run = QtCore.QProcess(self)
        self.process_run.readyRead.connect(self.dataReady)
       
        self.process_run.started.connect(lambda: self.ui.run_button.setEnabled(False))
        self.process_run.started.connect(lambda: self.ui.download_button.setEnabled(False))

        self.process_run.finished.connect(lambda: self.ui.run_button.setEnabled(True))
        self.process_run.finished.connect(lambda: self.ui.download_button.setEnabled(True))

        self.process_run.setProcessChannelMode(QtCore.QProcess.MergedChannels)

        # * Process and Signals for Download
        self.process_download = QtCore.QProcess(self)
        self.process_download.readyRead.connect(self.dataReady)
       
        self.process_download.started.connect(lambda: self.ui.run_button.setEnabled(False))
        self.process_download.started.connect(lambda: self.ui.download_button.setEnabled(False))

        self.process_download.finished.connect(lambda: self.ui.run_button.setEnabled(True))
        self.process_download.finished.connect(lambda: self.ui.download_button.setEnabled(True))

        self.process_download.setProcessChannelMode(QtCore.QProcess.MergedChannels)

        # * Variables
        self.genome_path = ''
        self.out_path = ''

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        # * Buttons
        # *     Paths
        self.ui.genomeBrowse_button.clicked.connect(self.on_push_genomeBrowse)
        self.ui.outBrowse_button.clicked.connect(self.on_push_outBrowse)
        # *     Run and Download
        self.ui.download_button.clicked.connect(self.on_push_download)
        self.ui.run_button.clicked.connect(self.on_push_run)

        # * Stream to capture print statements
        sys.stdout = Stream(newText=self.on_update_consoleOutput_textbrowser)

    def on_push_download(self):
        pass


    def on_push_run(self):
        pass

    def dataReady(self):
        cursor = self.ui.consoleOutput_textbrowser.textCursor()
        cursor.movePosition(cursor.End)
        Qbyte_stdout = (self.process.readAll())
        cursor.insertText(Qbyte_stdout.data().decode())
        self.ui.consoleOutput_textbrowser.setTextCursor(cursor)
        self.ui.consoleOutput_textbrowser.ensureCursorVisible()

    def on_update_consoleOutput_textbrowser(self, text):
        cursor = self.ui.consoleOutput_textbrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.consoleOutput_textbrowser.setTextCursor(cursor)
        self.ui.consoleOutput_textbrowser.ensureCursorVisible()


    def on_push_genomeBrowse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        # This might be useful for debugging, maybe cross platform? Need to test whether this is necessary
        # options |= QFileDialog.DontUseNativeDialog

        self.genome_path = QFileDialog.getExistingDirectory(
            self,  # this refers to a subclass of QWidget
            "Select Genome Data Folder",
            "",
            options=options,
        )

        if self.genome_path:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Genome Path Set!\n" + "Set to: ..." + self.genome_path + "\n"
            )
            self.ui.data_lineedit.insert(self.genome_path)

    def on_push_outBrowse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        # This might be useful for debugging, maybe cross platform? Need to test whether this is necessary
        # options |= QFileDialog.DontUseNativeDialog

        self.out_path = QFileDialog.getExistingDirectory(
            self,  # this refers to a subclass of QWidget
            "Select Download Folder",
            "",
            options=options,
        )

        if self.out_path:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Download Path Set!\n" + "Set to: ..." + self.out_path + "\n"
            )
            self.ui.data_lineedit.insert(self.out_path)

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()