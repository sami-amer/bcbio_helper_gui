from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from helper_gui import Ui_MainWindow
import sys


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        # * Path Variables
        self.dataPath = None
        self.gtfPath = None
        self.fastaPath = None
        self.outPath = None

        # * Option Variables
        self.analysis = None
        self.genome = None
        self.adapter = None
        self.strandedness = None
        self.aligner = None
        self.cores = None
        self.run_name = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # * Buttons
        # *     Paths
        self.ui.dataBrowse_button.clicked.connect(self.on_push_dataBrowse)
        self.ui.gtfBrowse_button.clicked.connect(self.on_push_gtfBrowse)
        self.ui.fastaBrowse_button.clicked.connect(self.on_push_fastaBrowse)
        self.ui.outBrowse_button.clicked.connect(self.on_push_outBrowse)
        # *     Options
        self.ui.save_button.clicked.connect(self.on_push_save)

    def on_push_dataBrowse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        # This might be useful for debugging, maybe cross platform? Need to test whether this is necessary
        # options |= QFileDialog.DontUseNativeDialog

        self.dataPath = QFileDialog.getExistingDirectory(
            self,  # this refers to a subclass of QWidget
            "Select RNA Data Folder",
            "",
            options=options,
        )

        if self.dataPath:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Path to RNA Data Set!\n" + "Set to: ..." + self.dataPath + "\n"
            )
            self.ui.data_lineedit.insert(self.dataPath)

    def on_push_gtfBrowse(self):
        options = QFileDialog.Options()

        self.gtfPath, _ = QFileDialog.getOpenFileName(
            self,
            "Select GTF File for Transciptome",
            "",
            "Gene Transfer Format (*.gtf)",
            options=options,
        )

        if self.gtfPath:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Path to GTF Set!\n" + "Set to: ..." + self.gtfPath + "\n"
            )
            self.ui.gtf_lineedit.insert(self.gtfPath)

    def on_push_fastaBrowse(self):
        options = QFileDialog.Options()

        self.fastaPath, _ = QFileDialog.getOpenFileName(
            self,
            "Select FASTA File for Transciptome",
            "",
            "FASTA format (*.fa)",
            options=options,
        )

        if self.fastaPath:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Path to FASTA Set!\n" + "Set to: ..." + self.fastaPath + "\n"
            )
            self.ui.fasta_lineedit.insert(self.fastaPath)

    def on_push_outBrowse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly

        self.outPath = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", "", options=options
        )

        if self.dataPath:
            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Output Folder Set!\n" + "Set to: ..." + self.outPath + "\n"
            )

            self.ui.out_lineedit.insert(self.outPath)

    def on_push_save(self):
        # TODO add checks for validity of each input, possibly against a set
        if self.analysis != self.ui.analysis_lineedit.text():

            self.analysis = self.ui.analysis_lineedit.text()

            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Updated Analysis to: " + self.analysis + "\n"
            )

        if self.genome != self.ui.genome_lineedit.text():

            self.genome = self.ui.genome_lineedit.text()

            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Updated Genome to: " + self.genome + "\n"
            )

        if self.adapter != self.ui.adapter_lineedit.text():

            self.adapter = self.ui.adapter_lineedit.text()

            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Updated adapter to: " + self.adapter + "\n"
            )

        if self.strandedness != self.ui.strand_lineedit.text():

            self.strandedness = self.ui.strand_lineedit.text()

            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Updated Strandedness to: " + self.strandedness + "\n"
            )

        if self.aligner != self.ui.aligner_lineedit.text():

            self.aligner = self.ui.aligner_lineedit.text()

            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Updated Aligner to: " + self.aligner + "\n"
            )

        if self.cores != self.ui.cores_lineedit.text():

            self.cores = self.ui.cores_lineedit.text()

            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Updated Core Count to:" + self.cores + "\n"
            )

        if self.run_name != self.ui.runName_lineedit.text():

            self.run_name = self.ui.runName_lineedit.text()

            self.ui.consoleOutput_textbrowser.insertPlainText(
                "Updated Core Count to: " + self.run_name + "\n"
            )


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    # ? Order of things to do
    # * DONE Get buttons to browse file system
    # TODO Implement option saving with save button, possibly without
    # TODO Print everything from console to the output box
    # TODO Add function to the run button
