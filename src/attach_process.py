from PyQt4 import QtCore, QtGui
import subprocess

class AttachProcessDialog(QtGui.QDialog):

    def __init__(self, parent=None):        

        QtGui.QDialog.__init__(self,parent)
        
        self.resize(617, 445)
        
        self.cmdAttach = QtGui.QPushButton('Attach',self)
        self.cmdAttach.setGeometry(QtCore.QRect(520, 410, 95, 31))
        self.connect(self.cmdAttach,QtCore.SIGNAL('clicked()'),self.cmdAttachClicked)
        
        self.cmdCancel = QtGui.QPushButton('Cancel',self)
        self.cmdCancel.setGeometry(QtCore.QRect(400, 410, 95, 31))
        self.connect(self.cmdCancel,QtCore.SIGNAL('clicked()'),self.cmdCancelClicked)
        
        self.listViewProcess = QtGui.QListWidget(self)
        self.listViewProcess.setGeometry(QtCore.QRect(3, 33, 611, 331))
        
        self.lineEditPid = QtGui.QLineEdit(self)
        self.lineEditPid.setGeometry(QtCore.QRect(159, 376, 113, 31))
        
        self.lblProcess = QtGui.QLabel('Process',self)
        self.lblProcess.setGeometry(QtCore.QRect(3, 6, 67, 21))
        
        self.lblPid = QtGui.QLabel('Enter PID of Porcess', self)
        self.lblPid.setGeometry(QtCore.QRect(5, 380, 151, 21))

        p = subprocess.Popen(['/bin/ps','-ef'],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        s = p.communicate()[0]

        split_s = s.split('\n')

        for i,x in enumerate(split_s):
            self.listViewProcess.insertItem(i,unicode(split_s[i],'utf-8'))

        self.listViewProcess.itemDoubleClicked.connect(self.listViewProcessDoubleClicked)
        
    def cmdAttachClicked(self):

        if str(self.lineEditPid.text())=="":
            ask = QtGui.QMessageBox.information(self,'Debugger','Please enter process pid',QtGui.QMessageBox.Ok)
            
        self.done(1)

    def cmdCancelClicked(self):

        self.done(0)

    def listViewProcessDoubleClicked(self,item):

        item_text = str(item.text())
        item_text_space_split = item_text.split(' ')
        for i,x in enumerate(item_text_space_split):
            if  x != '' and x!=' ':
                self.lineEditPid.setText(x.strip(' '))
                break
