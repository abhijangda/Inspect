from PyQt4 import QtCore, QtGui
import os

class OpenExecutableDialog(QtGui.QDialog):

    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        
        self.resize(546, 384)
        
        self.cmdOpen = QtGui.QPushButton('Open',self)
        self.cmdOpen.setGeometry(QtCore.QRect(444, 350, 95, 31))
        self.connect(self.cmdOpen,QtCore.SIGNAL('clicked()'),self.cmdOpenClicked)
        
        self.cmdCancel = QtGui.QPushButton('Cancel',self)
        self.cmdCancel.setGeometry(QtCore.QRect(337, 350, 95, 31))
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cmdCancelClicked)
        
        self.lblExecFile = QtGui.QLabel('Executable File',self)
        self.lblExecFile.setGeometry(QtCore.QRect(5, 3, 111, 21))
        
        self.entryExecutable = QtGui.QLineEdit(self)
        self.entryExecutable.setGeometry(QtCore.QRect(4, 30, 477, 31))
        
        self.cmdExec = QtGui.QPushButton('...',self)
        self.cmdExec.setGeometry(QtCore.QRect(487, 30, 53, 30))
        self.connect(self.cmdExec,QtCore.SIGNAL('clicked()'),self.cmdExecClicked)
        
        self.lblWorkingDir = QtGui.QLabel('Working Directory',self)
        self.lblWorkingDir.setGeometry(QtCore.QRect(5, 70, 121, 21))
        
        self.entryWorking = QtGui.QLineEdit(self)
        self.entryWorking.setGeometry(QtCore.QRect(4, 95, 478, 31))
        
        self.cmdDir = QtGui.QPushButton('...',self)
        self.cmdDir.setGeometry(QtCore.QRect(487, 95, 54, 31))
        self.connect(self.cmdDir,QtCore.SIGNAL('clicked()'),self.cmdDirClicked)
        
        self.entryArg = QtGui.QLineEdit(self)
        self.entryArg.setGeometry(QtCore.QRect(4, 156, 535, 31))
        
        self.lblArg = QtGui.QLabel('Arguments',self)
        self.lblArg.setGeometry(QtCore.QRect(8, 130, 81, 21))
        
        self.lblEnv = QtGui.QLabel('Environment Variables',self)
        self.lblEnv.setGeometry(QtCore.QRect(6, 196, 151, 21))
        
        self.envVarView = QtGui.QTableWidget(self)
        self.envVarView.setGeometry(QtCore.QRect(4, 220, 433, 121))
        
        self.envVarView.setColumnCount(2)
        self.envVarView.setHorizontalHeaderLabels(['Name','Value'])
        self.envVarView.setRowCount(1)
        
        self.cmdAdd = QtGui.QPushButton('Add',self)
        self.cmdAdd.setGeometry(QtCore.QRect(445, 230, 95, 31))
        self.connect(self.cmdAdd,QtCore.SIGNAL('clicked()'),self.cmdAddClicked)
        
        self.cmdRemove = QtGui.QPushButton('Remove',self)
        self.cmdRemove.setGeometry(QtCore.QRect(445, 280, 95, 31))
        self.connect(self.cmdRemove,QtCore.SIGNAL('clicked()'),self.cmdRemoveClicked)

    def cmdOpenClicked(self):

        if str(self.entryExecutable.text())!="":
            if os.path.exists(str(self.entryExecutable.text()))==False:
                ask = QtGui.QMessageBox.information(self,'Debugger','Executable File entered doesn\'t exists',QtGui.QMessageBox.Ok)
                return
            if str(self.entryWorking.text())!="" and os.path.exists(str(self.entryWorking.text()))==False:
                ask = QtGui.QMessageBox.information(self,'Debugger','Working Directory entered doesn\'t exists',QtGui.QMessageBox.Ok)
                return
            self.done(1)
        else:
            ask = QtGui.QMessageBox.information(self,'Debugger','Please enter executable file',QtGui.QMessageBox.Ok)

    def cmdCancelClicked(self):

        self.done(0)

    def cmdExecClicked(self):

        filename = str(QtGui.QFileDialog.getOpenFileName(self,'Open File'))
        if filename!="":
            self.entryExecutable.setText(filename)

    def cmdDirClicked(self):

        filename = str(QtGui.QFileDialog.getExistingDirectory(self,'Working Directory',"",QtGui.QFileDialog.ShowDirsOnly))
        if filename!="":
            self.entryWorking.setText(filename)

    def cmdAddClicked(self):

        self.envVarView.insertRow(self.envVarView.rowCount())

    def cmdRemoveClicked(self):

        self.envVarView.removeRow(self.envVarView.currentRow())
