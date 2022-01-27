from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QThreadPool, QRunnable, pyqtSlot, pyqtSignal
from gui_helper import Ui_MainWindow
import func_helper
import sys, subprocess


class Stream(QtCore.QObject):
    # * Stream object for console output text
    newText = QtCore.pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))
    
    def flush(self):
        # ? Flush must be implemented, but it can be a no-op
        pass

class WorkerSignals(QObject):
    
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    # result = pyqtSignal()
    progress = pyqtSignal(str)

class Worker(QRunnable):

    
    def __init__(self,*args,**kwargs): # removed fn from here
        super(Worker, self).__init__()
        # self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        arguments = self.args[0]
        
        for output in self.execute(arguments):
            # print(output, end="")
            self.signals.progress.emit(output) 
        self.signals.finished.emit()


    # ---- Adapted from StackOverflow
    # ---- https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    def execute(self,cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line 
        popen.stdout.close()
        return_code = popen.wait()
        if return_code: # ! Replace this with something that ends the subprocess without hanging
            raise subprocess.CalledProcessError(return_code, cmd) 
            # print("FAILED!")
    # ----
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
        self.ui.runButton_button.clicked.connect(self.on_push_run)
        # *     Options
        self.ui.save_button.clicked.connect(self.on_push_save)

        # * Stream for Console Output
        sys.stdout = Stream(newText=self.on_update_consoleOutput_textbrowser)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def on_update_consoleOutput_textbrowser(self, text):
        cursor = self.ui.consoleOutput_textbrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.consoleOutput_textbrowser.setTextCursor(cursor)
        self.ui.consoleOutput_textbrowser.ensureCursorVisible()

    def store_arguments(self):
        # arguments = { # this approach is for the function version
        #     "analysis": self.analysis,
        #     "genome": self.genome,
        #     "aligner": self.aligner,
        #     "adapter": self.adapter,
        #     "strandedness": self.strandedness,
        #     "fasta_path": self.fastaPath,
        #     "gtf_path": self.gtfPath,
        #     "outpath": self.outPath,
        #     "cores": self.cores,
        #     "run_name": self.run_name,
        #     "data_path": self.dataPath
        # }

        arguments = [
            "python3",
            "bcbio_helper.py",
            self.dataPath,
            self.fastaPath,
            self.gtfPath,
            "--analysis",
            self.analysis if self.analysis else "RNA-seq",
            "--genome",
            self.genome if self.genome else "hg38",
            "--aligner",
            self.aligner if self.aligner else "hisat2",
            "--adapter",
            self.adapter if self.adapter else "polya",
            "--strandedness",
            self.strandedness if self.strandedness else "unstranded",
            "--cores",
            self.cores if self.cores else "12",
            self.run_name if self.run_name else "unnamed",
            self.outPath # ! make sure this is correct
        ]

        return arguments
    
    def progress_fn(self, progress):
        print(str(progress))
        
    def on_push_run(self):
        arguments = self.store_arguments()
        # TODO: Make this a call to the Worker
        # print("args",arguments)
        # for output in self.execute(arguments):
        #     print(output, end="")
        
        # with subprocess.Popen(arguments, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        #     for line in p.stdout:
        #         print(line, end='') # process line here

        # if p.returncode != 0:
        #     raise subprocess.CalledProcessError(p.returncode, p.args)

        worker = Worker(arguments) # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        # Execute
        self.threadpool.start(worker)
        


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
                "Updated Run Name to: " + self.run_name + "\n"
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
    # * DONE Implement option saving with save button, possibly without
    # TODO Print everything from console to the output box
    # * DONE Add function to the run button
