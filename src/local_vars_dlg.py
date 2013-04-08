from PyQt4 import QtCore, QtGui

class LocalVarsDialog(QtGui.QDialog):
    
    def __init__(self, parent=None):

        QtGui.QDialog.__init__(self,parent)
        self.resize(565, 300)
        self.treeWidget = QtGui.QTreeWidget(self)
        self.treeWidget.setGeometry(QtCore.QRect(2, 3, 561, 291))

        self.treeWidget.setColumnCount(3)
        self.treeWidget.setHeaderLabels(['Name','Type','Value'])        
        self.exp_type=""
        self.exp_value=""
        self.struct_inspected=False
        self.treeWidgetItemList=[]
        
    def setExpData(self,exp_name, exp_value,exp_type):

        exp_type=exp_type[exp_type.find('=')+1:]
        exp_type=exp_type.strip()

        self.treeWidgetItem = QtGui.QTreeWidgetItem(self.treeWidget)
        self.treeWidgetItem.setText(0,exp_name)
        self.treeWidgetItem.setText(2,exp_value)
        self.treeWidgetItem.setText(1,exp_type)

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
