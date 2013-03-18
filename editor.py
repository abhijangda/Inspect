from PyQt4 import QtCore, QtGui

class CodeWidget(QtGui.QWidget):

    class NumberBar(QtGui.QWidget):

        def __init__(self, parent= None, *args):
            
            QtGui.QWidget.__init__(self, parent,*args)
            self.edit = None            
            self.highest_line = 0            
            self.parent = parent
            
        def setTextEdit(self, edit):
            
            self.edit = edit
            
        def mouseReleaseEvent(self, mouse_event):

            QtGui.QWidget.mouseReleaseEvent(self,mouse_event)
            
        def update(self, *args):
            
            width = self.fontMetrics().width(str(self.highest_line)) + 7
            if self.width() != width:
                self.setFixedWidth(width)
            QtGui.QWidget.update(self, *args)
 
        def paintEvent(self, event):
            
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursorWithHiddenText().position())
            block_count = self.edit.document().blockCount()            
            painter = QtGui.QPainter(self)

            block = current_block
            line_count_prev = block.blockNumber()+1            
                
            while block.isValid():               
                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()                            
                if position.y() < contents_y:
                    break                
                block = block.previous()               
                
            if not block.isValid():
                block = self.edit.document().findBlock(0)
            line_count_next = block.blockNumber()
            count = 0            
            
            begining_block= block
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()            
            
            while block.isValid() and position.y() <= page_bottom:
                
                line_count_next += 1                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()

                if position.y() >= contents_y and position.y() <=page_bottom:
                    bold = False
                    
                    ##For updating line numbers
                    for i,x in enumerate(self.parent.txtInput.hidden_text_array):
                        if block.position()>x.start_pos and i not in self.added_array:
                            self.added_array.append(i)
                            line_count_next += x.get_number_of_lines()
                    #########################                    
                        
                block = block.next()               
            
            painter.end()
            QtGui.QWidget.paintEvent(self, event)

    def __init__(self,projtype,parent=None):

        QtGui.QWidget.__init__(self,parent)
        
        self.txtInput = QtGui.QTextEdit(self) 

        self.number_bar = self.NumberBar(self)
        self.number_bar.setTextEdit(self.txtInput)
        
        self.hbox_textedit = QtGui.QHBoxLayout(self)
        self.hbox_textedit.setSpacing(0)
        self.hbox_textedit.setMargin(0)
        self.hbox_textedit.addWidget(self.number_bar)
        self.hbox_textedit.addWidget(self.txtInput)
        
        self.setLayout(self.hbox_textedit)


    
