from PyQt4 import QtCore, QtGui
import syntaxcpp

BREAKPOINT_STATE_ENABLED = 1
BREAKPOINT_STATE_DISABLED = 2

class Breakpoint(object):

    def __init__(self,line,state,filename):

        self.line_number = line
        self.state = state
        self.filename = filename

class SourceEdit(QtGui.QTextEdit):

    def __init__(self,parent=None):

        QtGui.QTextEdit.__init__(self,parent)

        self.parent=parent
        self.list_extra_selections = []
        self.list_lines_highlighted=[]
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        
    def highlight_line(self,line):

        try:
            index = self.list_lines_highlighted.index(line)
            extra_selection = self.list_extra_selections[index]
            extra_selection.format.setBackground(QtGui.QColor(255,255,255))
        except ValueError:
            extra_selection = QtGui.QTextEdit.ExtraSelection()
            extra_selection.cursor = self.textCursor()            
            if line > extra_selection.cursor.blockNumber():
                extra_selection.cursor.movePosition(QtGui.QTextCursor.Down,QtGui.QTextCursor.MoveAnchor,line-extra_selection.cursor.blockNumber()-2)
            if line < extra_selection.cursor.blockNumber():
                extra_selection.cursor.movePosition(QtGui.QTextCursor.Up,QtGui.QTextCursor.MoveAnchor,extra_selection.cursor.blockNumber()-line-2)
            extra_selection.cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            extra_selection.cursor.movePosition(QtGui.QTextCursor.EndOfLine,QtGui.QTextCursor.KeepAnchor)
            extra_selection.format.setBackground(QtGui.QColor(0,255,0))
            self.list_extra_selections.append(extra_selection)
            self.setExtraSelections(self.list_extra_selections)
            self.list_lines_highlighted.append(line)
        
class CodeWidget(QtGui.QWidget):

    class NumberBar(QtGui.QWidget):

        def __init__(self, parent= None, *args):
            
            QtGui.QWidget.__init__(self, parent,*args)
            self.edit = None            
            self.highest_line = 0            
            self.parent = parent
            self.first_line = 0
            self.acceptBreakpoints = True
            
        def setTextEdit(self, edit):
            
            self.edit = edit
            
        def mouseReleaseEvent(self, mouse_event):           

            if self.acceptBreakpoints==False:
                QtGui.QWidget.mouseReleaseEvent(self,mouse_event)
                return
            
            line = -1
            for i in range(len(self.list_draw_text_y)-1,-1,-1):

                if mouse_event.y() >= self.list_draw_text_y[i][0]-self.fontMetrics().ascent():
                    line = self.list_draw_text_y[i][1]
                    break            
            
            if line!=-1:
                found = False
                breakpoint = Breakpoint(0,0,"")
                for breakpoint in self.parent.list_breakpoints:
                    if int(breakpoint.line_number)==line:
                        found = True
                        break
                if found==True:
                    if breakpoint.state == BREAKPOINT_STATE_DISABLED:
                        breakpoint.state = BREAKPOINT_STATE_ENABLED
                    else:
                        breakpoint.state = BREAKPOINT_STATE_DISABLED
                    self.parent.breakpointChange(breakpoint)
                else:
                    self.parent.list_breakpoints.append(Breakpoint(line,BREAKPOINT_STATE_ENABLED,self.parent.filename))                    
                    self.parent.sendSetBreakpointSignal(line)
                self.repaint()
                
            QtGui.QWidget.mouseReleaseEvent(self,mouse_event)
            
        def update(self, *args):
            
            width = self.fontMetrics().width(str(self.highest_line)) + 27
            if self.width() != width:
                self.setFixedWidth(width)
            
            QtGui.QWidget.update(self, *args)
 
        def paintEvent(self, event):
            
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())
            block_count = self.edit.document().blockCount()            
            painter = QtGui.QPainter(self)

            block = current_block
            line_count_prev = block.blockNumber()+1            
            self.list_draw_text_y = []
            
            while block.isValid():               
                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
                if position.y() < contents_y:
                    break                
                block = block.previous()               
                
            if not block.isValid():
                block = self.edit.document().findBlock(0)
            line_count_next = block.blockNumber()
            self.first_line= line_count_next
            count = 0            
            
            begining_block= block
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()            
            
            while block.isValid() and position.y() <= page_bottom:                
                line_count_next += 1                
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
                
                if position.y() >= contents_y and position.y() <=page_bottom:
                    bold = False
                    pen = painter.pen()                   
                    painter.setPen(pen)
                    if block == current_block:
                        bold = True
                        font = painter.font()
                        font.setBold(True)
                        painter.setFont(font)
                    painter.drawText(1, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count_next))
                    self.list_draw_text_y.append((round(position.y()) - contents_y + font_metrics.ascent(),line_count_next))
                    if bold:
                        font = painter.font()
                        font.setBold(False)
                        painter.setFont(font)

                found = False
                breakpoint = Breakpoint(0,0,"")
                for breakpoint in self.parent.list_breakpoints:                    
                    if int(breakpoint.line_number)==line_count_next:
                        found = True
                        break
                
                if found==True:
                    
                    if breakpoint.state == BREAKPOINT_STATE_ENABLED:                        
                        point = QtCore.QPoint(self.fontMetrics().width(str(self.highest_line))+5,round(position.y())-contents_y+2)
                        rect = QtCore.QRect(0,0,self.width()-self.fontMetrics().width(str(self.highest_line)),self.fontMetrics().height())
                        painter.drawImage(point,QtGui.QImage("./breakpoint-enable1.png"),rect)
                    if breakpoint.state == BREAKPOINT_STATE_DISABLED:
                        point = QtCore.QPoint(self.fontMetrics().width(str(self.highest_line))+5,round(position.y())-contents_y+2)
                        rect = QtCore.QRect(0,0,self.width()-self.fontMetrics().width(str(self.highest_line)),self.fontMetrics().height())
                        painter.drawImage(point,QtGui.QImage("./breakpoint-disable1.png"),rect)
                if self.parent.drawLinePointer==True:

                    if self.parent.linePointer==line_count_next:
                        point = QtCore.QPoint(self.fontMetrics().width(str(self.highest_line))+5,round(position.y())-contents_y+2)
                        rect = QtCore.QRect(0,0,self.width()-self.fontMetrics().width(str(self.highest_line)),self.fontMetrics().height())
                        painter.drawImage(point,QtGui.QImage("./arrow.png"),rect)
                        
                block = block.next()               
            self.highest_line = line_count_next
            painter.end()
            QtGui.QWidget.paintEvent(self, event)

    def __init__(self,parent=None):

        QtGui.QWidget.__init__(self,parent)
        
        self.txtInput = SourceEdit(self)

        self.number_bar = self.NumberBar(self)
        self.number_bar.setTextEdit(self.txtInput)
        
        self.hbox_textedit = QtGui.QHBoxLayout(self)
        self.hbox_textedit.setSpacing(0)
        self.hbox_textedit.setMargin(0)
        self.hbox_textedit.addWidget(self.number_bar)
        self.hbox_textedit.addWidget(self.txtInput)
        
        self.setLayout(self.hbox_textedit)

        self.txtInput.installEventFilter(self)
        self.txtInput.viewport().installEventFilter(self)

        highlight = syntaxcpp.CPPHighlighter(self.txtInput.document())
        self.filename=""
        self.list_draw_text_y = []
        self.list_breakpoints=[]
        self.filepath = ""
        self.drawLinePointer = False
        self.linePointer=-1
        
    def setLinePointerAtLine(self,line):

        self.linePointer=line
        self.drawLinePointer = True
        
    def open_file(self,filepath):

        try:            
            f = open(filepath,'r')
            s = ""
            for d in f:
                s+=d

            self.txtInput.setText(s)
            self.filepath=filepath
            return 1
        except IOError:
            return -1
        
    def eventFilter(self, object, event):
                
        if object in (self.txtInput, self.txtInput.viewport()):
            self.number_bar.update()
            return False
        return QtGui.QWidget.eventFilter(object, event)

    def addBreakpoint(self,breakpoint):

        self.list_breakpoints.append(Breakpoint(breakpoint.line,1,breakpoint.filename))        
            
    def breakpointChange(self,breakpoint):

        self.emit(QtCore.SIGNAL('breakpointStateChanged(int,int)'),int(breakpoint.line_number),int(breakpoint.state))
        
    def disableAllBreakpoints(self):

        for b in self.list_breakpoints:
            b.state=2
            
    def enableAllBreakpoints(self):

        for b in self.list_breakpoints:
            b.state=1

    def sendSetBreakpointSignal(self,line):

        self.emit(QtCore.SIGNAL('setBreakpoint(int)'),line)
