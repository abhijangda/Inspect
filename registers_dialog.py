from PyQt4 import QtGui,QtCore
import re

class RegistersDialog(QtGui.QDialog):

    def __init__(self,parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle('Registers')
        
        self.setGeometry(0,0,400,300)
        self.listView = QtGui.QListWidget(self)
        self.listView.setGeometry(0,0,400,300)

    def setString(self,string):

        for i,s in enumerate(re.findall(r'.+',string)):
            if s.find('Type <return> to continue')!=-1 or s.find('(gdb)')!=-1:
                continue
            
            if s.find('value not available')==-1:
                s = s[:s.rfind('\t')]
            
            s=s.strip()
            self.listView.insertItem(i,unicode(s,'utf-8'))  
