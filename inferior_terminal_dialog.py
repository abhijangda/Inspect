from PyQt4 import QtCore,QtGui
import terminal_text_edit

class InferiorTerminalTextEdit(terminal_text_edit.TerminalTextEdit):

    def __init__(self,parent=None):

        terminal_text_edit.TerminalTextEdit.__init__(self,parent)

    def appendOutput(self,text):

        cc = self.textCursor()
        self.append(text)
        self.min_pos = cc.position()
        self.setTextCursor(cc)

    def runCommand(self,command):

        self.appendOutput(command)
        self.emit(QtCore.SIGNAL('writeCommand(QString)'),command+'\n')

class InferiorTerminalDialog(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)

        self.terminal_text_edit = InferiorTerminalTextEdit(self)
        #self.setCentralWidget(self.terminal_text_edit)
        self.setGeometry(100,100,400,300)
        self.terminal_text_edit.setGeometry(0,0,400,300)
        self.setWindowTitle('Process Terminal')
        
    def show_dialog(self):

        self.show()
        self.terminal_text_edit.setText("")
