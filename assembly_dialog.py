from PyQt4 import QtCore, QtGui
import source_editor

class AssemblyDialog(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle("Assembly")

        self.textView = source_editor.CodeWidget(self)
        self.textView.number_bar.acceptBreakpoints=False
        self.setGeometry(0,0,400,300)
        self.textView.setGeometry(0,0,400,300)

    def setText(self,string):

        string = string.replace('(gdb)','')
        arrow_index = string.find("=>")
        string = string.replace("=>",'')
        self.textView.txtInput.setText(string)        
        cursor = self.textView.txtInput.textCursor()
        cursor.setPosition(arrow_index)
        self.textView.setLinePointerAtLine(cursor.blockNumber()+1)
