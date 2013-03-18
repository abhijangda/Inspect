from PyQt4 import QtCore, QtGui

class InspectExpressionDialog(QtGui.QDialog):

    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        
        self.resize(396, 215)
        
        self.treeWidget = QtGui.QTreeWidget(self)
        self.treeWidget.setGeometry(QtCore.QRect(2, 39, 393, 174))
        
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setHeaderLabels(['Name','Type','Value'])
        
        self.lineEditExp = QtGui.QLineEdit(self)
        self.lineEditExp.setGeometry(QtCore.QRect(84, 3, 211, 31))
        
        self.lblExp = QtGui.QLabel("Expression",self)
        self.lblExp.setGeometry(QtCore.QRect(7, 7, 71, 21))
                
        self.cmdInspect = QtGui.QPushButton("Inspect",self)
        self.cmdInspect.setGeometry(QtCore.QRect(299, 3, 95, 31))

        self.connect(self.cmdInspect,QtCore.SIGNAL('clicked()'),self.cmdInspectClicked)
        self.exp_val = ""
        self.exp_type=""
        self.treeWidgetItemList = []
        self.struct_inspected = False
        
    def cmdInspectClicked(self):

        self.emit(QtCore.SIGNAL('inspectVariable(QString)'),self.lineEditExp.text())

    def cmdCancelClicked(self):

        self.done(0)

    def setExpData(self,exp_value,exp_type):

        if exp_value!="":
            self.exp_val=exp_value
        
        if exp_type!="":
            self.exp_type=exp_type

        self.exp_val=self.exp_val.strip()
        self.exp_type=self.exp_type.strip()
        
        if self.exp_val=="" or self.exp_type=="":
            return
        
        if '{' in self.exp_val and '}' in self.exp_val:
            self.exp_val = self.exp_val[self.exp_val.find('=')+1:]
            self.exp_val=self.exp_val.strip()
            self.exp_type = self.exp_type[self.exp_type.find('=')+1:]
            self.exp_type=self.exp_type.strip()
            if self.struct_inspected == False:
                self.emit(QtCore.SIGNAL('inspectStruct(QString)'),QtCore.QString(self.exp_val))
                self.struct_inspected=True
        else:
            self.exp_val=self.exp_val[self.exp_val.find('=')+1:]
            self.exp_val=self.exp_val.strip()
            
            self.exp_type=self.exp_type[self.exp_type.find('=')+1:]
            self.exp_type=self.exp_type.strip()

            self.treeWidgetItem = QtGui.QTreeWidgetItem(self.treeWidget)
            self.treeWidgetItem.setText(0,self.lineEditExp.text())
            self.treeWidgetItem.setText(1,self.exp_val)
            self.treeWidgetItem.setText(2,self.exp_type)

    def setStructData(self,var):

        if var.parent==None:
            self.treeWidgetItem = QtGui.QTreeWidgetItem(self.treeWidget)
            self.treeWidgetItemList.append(self.treeWidgetItem)
            self.treeWidgetItem.setText(0,var.name)
            self.treeWidgetItem.setText(2,var.val)
            _type= var.type[var.type.find('=')+1:]
            _type=_type.strip()
            self.treeWidgetItem.setText(1,_type)
        else:
            for item in self.treeWidgetItemList:
                if item.text(0) == var.parent.name:
                    self.treeWidgetItem = QtGui.QTreeWidgetItem(item)
                    self.treeWidgetItemList.append(self.treeWidgetItem)
                    self.treeWidgetItem.setText(0,var.name)
                    self.treeWidgetItem.setText(2,var.val)
                    _type= var.type[var.type.find('=')+1:]
                    _type=_type.strip()  
                    self.treeWidgetItem.setText(1,_type)
                    break
                
        for v in var.list_variables:
            self.setStructData(v)
