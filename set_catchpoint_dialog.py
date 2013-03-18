from PyQt4 import QtCore, QtGui

class SetCatchpointDialog(QtGui.QDialog):
    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        
        self.resize(371, 246)
        
        self.rbThrow = QtGui.QRadioButton("Throw Exception",self)
        self.rbThrow.setGeometry(QtCore.QRect(40, 39, 141, 26))
        self.rbThrow.setChecked(True)
        
        self.rbCatch = QtGui.QRadioButton("Catch Exception",self)
        self.rbCatch.setGeometry(QtCore.QRect(40, 69, 131, 26))

        self.rbExec = QtGui.QRadioButton("Exec",self)
        self.rbExec.setGeometry(QtCore.QRect(40, 103, 61, 26))

        self.rbSystemCall = QtGui.QRadioButton("System Call",self)
        self.rbSystemCall.setGeometry(QtCore.QRect(40, 135, 101, 26))

        self.lineEditSysCall = QtGui.QLineEdit(self)
        self.lineEditSysCall.setGeometry(QtCore.QRect(247, 166, 122, 31))

        self.lblEvent = QtGui.QLabel("Event",self)
        self.lblEvent.setGeometry(QtCore.QRect(20, 15, 67, 21))

        self.lblSysCall = QtGui.QLabel("System Call Number/Name",self)
        self.lblSysCall.setGeometry(QtCore.QRect(63, 169, 181, 21))

        self.cmdSet = QtGui.QPushButton("Set Catchpoint",self)
        self.cmdSet.setGeometry(QtCore.QRect(274, 209, 95, 31))

        self.cmdCancel = QtGui.QPushButton("Cancel",self)
        self.cmdCancel.setGeometry(QtCore.QRect(170, 209, 95, 31))
        
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cmdCancelClicked)
        self.connect(self.cmdSet,QtCore.SIGNAL('clicked()'),self.cmdSetClicked)
        
    def cmdSetClicked(self):

        self.done(1)
        
    def cmdCancelClicked(self):

        self.done(0)
