from PyQt4 import QtCore, QtGui
        
from inspect_expression_dialog import *

class SetWatchpointDialog(InspectExpressionDialog):

    def __init__(self,parent):

        InspectExpressionDialog.__init__(self,parent)
        self.resize(400, 292)

        self.cbRead = QtGui.QCheckBox("Read",self)
        self.cbRead.setGeometry(QtCore.QRect(6, 227, 141, 26))
        
        self.cbWrite = QtGui.QCheckBox("Write",self)
        self.cbWrite.setGeometry(QtCore.QRect(176, 227, 141, 26))
        
        self.cmdSet = QtGui.QPushButton("Set",self)
        self.cmdSet.setGeometry(QtCore.QRect(297, 259, 95, 31))
        
        self.cmdCancel = QtGui.QPushButton("Cancel",self)
        self.cmdCancel.setGeometry(QtCore.QRect(187, 259, 95, 31))

        self.connect(self.cmdSet,QtCore.SIGNAL('clicked()'),self.cmdSetClicked)
        
    def cmdSetClicked(self):

        self.emit(QtCore.SIGNAL('setWatchpoint()'))

    def cmdCancelClicked(self):

        self.done(0)
