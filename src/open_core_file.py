from PyQt4 import QtCore, QtGui

class OpenCoreFileDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        
        QtGui.QDialog.__init__(self,parent)
        
        self.resize(546, 172)
        self.cmdOpen = QtGui.QPushButton('Open',self)
        self.cmdOpen.setGeometry(QtCore.QRect(446, 135, 95, 31))
        self.connect(self.cmdOpen,QtCore.SIGNAL('clicked()'),self.cmdOpenClicked)
        
        self.cmdCancel = QtGui.QPushButton('Cancel',self)
        self.cmdCancel.setGeometry(QtCore.QRect(339, 135, 95, 31))
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cmdCancelClicked)
        
        self.lblExec = QtGui.QLabel('Executable File',self)
        self.lblExec.setGeometry(QtCore.QRect(5, 3, 111, 21))
        
        self.lineEditExec = QtGui.QLineEdit(self)
        self.lineEditExec.setGeometry(QtCore.QRect(4, 30, 477, 31))
        
        self.toolButtonExec = QtGui.QToolButton(self)
        self.toolButtonExec.setGeometry(QtCore.QRect(487, 30, 53, 30))
        self.connect(self.toolButtonExec,QtCore.SIGNAL('clicked()'),self.cmdExecClicked)

        self.lblCore = QtGui.QLabel('Core File',self)
        self.lblCore.setGeometry(QtCore.QRect(5, 70, 121, 21))
        
        self.lineEditCore = QtGui.QLineEdit(self)
        self.lineEditCore.setGeometry(QtCore.QRect(4, 95, 478, 31))
        
        self.toolButtonCore = QtGui.QToolButton(self)
        self.toolButtonCore.setGeometry(QtCore.QRect(487, 95, 54, 31))
        self.connect(self.toolButtonCore,QtCore.SIGNAL('clicked()'),self.cmdCoreFileClicked)

    def cmdOpenClicked(self):

        if str(self.lineEditExec.text())=="":
            ask = QtGui.QMessageBox.information(self,'Debugger','Please enter executable file',QtGui.QMessageBox.Ok)
            return
        
        if os.path.exists(str(self.lineEditExec.text()))==False:
            ask = QtGui.QMessageBox.information(self,'Debugger','Executable File entered doesn\'t exists',QtGui.QMessageBox.Ok)
            return

        if str(self.lineEditCore.text())=="":
            ask = QtGui.QMessageBox.information(self,'Debugger','Please enter core file',QtGui.QMessageBox.Ok)
            return
        
        if os.path.exists(str(self.lineEditCore.text()))==False:
            ask = QtGui.QMessageBox.information(self,'Debugger','Core File entered doesn\'t exists',QtGui.QMessageBox.Ok)
            return
        
        self.done(1)

    def cmdExecClicked(self):

        filename = str(QtGui.QFileDialog.getOpenFileName(self,'Open File'))
        if filename!="":
            self.lineEditExec.setText(filename)

    def cmdCoreFileClicked(self):

        filename = str(QtGui.QFileDialog.getOpenFileName(self,'Open File'))
        if filename!="":
            self.lineEditCore.setText(filename)

    def cmdCancelClicked(self):

        self.done(0)
