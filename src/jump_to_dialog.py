from PyQt4 import QtCore, QtGui

class JumpToDialog(QtGui.QDialog):

    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        
        self.resize(282, 262)
        
        self.lblFileName = QtGui.QLabel("File Name",self)
        self.lblFileName.setGeometry(QtCore.QRect(35, 80, 67, 21))
        
        self.rbAddress = QtGui.QRadioButton("Memory Address",self)
        self.rbAddress.setGeometry(QtCore.QRect(5, 173, 141, 26))
        
        self.lblLine = QtGui.QLabel("Line Number",self)
        self.lblLine.setGeometry(QtCore.QRect(35, 128, 81, 21))
        
        self.lineEditFile = QtGui.QLineEdit(self)
        self.lineEditFile.setGeometry(QtCore.QRect(165, 77, 113, 31))
        
        self.lineEditLine = QtGui.QLineEdit(self)
        self.lineEditLine.setGeometry(QtCore.QRect(165, 124, 113, 31))
        
        self.lineEditAddress = QtGui.QLineEdit(self)
        self.lineEditAddress.setGeometry(QtCore.QRect(165, 171, 113, 31))
        
        self.rbSourceFile = QtGui.QRadioButton("Source File",self)
        self.rbSourceFile.setGeometry(QtCore.QRect(5, 40, 108, 26))
        
        self.rbFunction = QtGui.QRadioButton("Function",self)
        self.rbFunction.setGeometry(QtCore.QRect(5, 8, 108, 26))
        
        self.lineEditFunc = QtGui.QLineEdit(self)
        self.lineEditFunc.setGeometry(QtCore.QRect(165, 6, 113, 31))
        
        self.cmdJump = QtGui.QPushButton("Jump",self)
        self.cmdJump.setGeometry(QtCore.QRect(184, 226, 95, 31))
        self.connect(self.cmdJump,QtCore.SIGNAL('clicked()'),self.cmdJumpClicked)
        
        self.cmdCancel = QtGui.QPushButton("Cancel",self)
        self.cmdCancel.setGeometry(QtCore.QRect(78, 226, 95, 31))
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cmdCancelClicked)

    def cmdJumpClicked(self):

        self.done(1)

    def cmdCancelClicked(self):

        self.done(0)
