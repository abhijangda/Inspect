from PyQt4 import QtCore, QtGui
import sys
import terminal_text_edit
from gdb_reading_thread import *
from PyQt4 import QtGui,QtCore
import sip,sys,os,pty,time
import select,fcntl,termios,re
import open_executable,open_core_file,attach_process,source_editor,inferior_terminal_dialog
import set_breakpoint,inspect_expression_dialog,set_watchpoint_dialog,set_catchpoint_dialog
from breakpoints import *
import local_vars_dlg,registers_dialog,assembly_dialog,breakpoints_dialog,jump_to_dialog
import global_vars_dlg

class VariableTree(object):

    def __init__(self,_name,_val,_type,_parent):

        self.name=_name
        self.val= _val
        self.type=_type

        self.list_variables = []
        self.parent = _parent
        self.scope_name=self.name
        if self.parent!=None:
            self.scope_name = _parent.scope_name + "." + self.name        

    def get_var_from_name(self,var_name):
        
        if self.name==var_name:
            return self

        found = None
        for var in self.list_variables:
            if var.get_var_from_name(var_name)==None:
                return None
            else:
                found = var.get_var_from_name(var_name)
                break

        if found != None:
            return found
    
class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, parent=None):

######Creating the psuedoterminal and child process###########
        return_val = pty.fork()

        if return_val[0]==0:

            os.execv("/bin/bash",["/bin/bash"])

        self.state = 0
        self.fd = return_val[1]
        tc_attr = termios.tcgetattr(self.fd)
        tc_attr[3] = tc_attr[3] & ~termios.ECHO
        termios.tcsetattr(self.fd,termios.TCSANOW,tc_attr)
        fl = fcntl.fcntl(self.fd,fcntl.F_GETFL)
        fcntl.fcntl(self.fd,fcntl.F_SETFL,fl|os.O_NONBLOCK)
################################################################

        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("Debugger")
        self.resize(800, 600)
        
        self.tabFile = QtGui.QTabWidget(self)
        self.tabFile.setGeometry(QtCore.QRect(0, 0, 800, 391))
        self.setCentralWidget(self.tabFile)
        self.list_code_widget=[]
        self.list_file_old_new=[]
        self.inferior_terminal_dialog = inferior_terminal_dialog.InferiorTerminalDialog(self)
        self.connect(self.inferior_terminal_dialog.terminal_text_edit,QtCore.SIGNAL('writeCommand(QString)'),self.writeCommand)
        self.direct_to_inferior_terminal=False        
        self.list_local_vars=[]
        
#####Creating Menubars#########################################
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 29))
        
        self.menuFile = QtGui.QMenu('File',self.menubar)        
        self.menuRun = QtGui.QMenu('Run',self.menubar)        
        self.menuBreakpoints = QtGui.QMenu('Breakpoints',self.menubar)        
        self.menuNavigate = QtGui.QMenu('Navigate',self.menubar)        
        self.menuExpression = QtGui.QMenu('Expression',self.menubar)        
        self.menuView = QtGui.QMenu('View',self.menubar)
        
        self.setMenuBar(self.menubar)       

######File menu actions#########################
        self.actionOpen_Executable_File = QtGui.QAction('Open Executable',self)
        self.connect(self.actionOpen_Executable_File,QtCore.SIGNAL('triggered()'),self.openExecutableTriggered)
        
        self.actionOpenCoreFile = QtGui.QAction('Open Core File',self)
        self.connect(self.actionOpenCoreFile,QtCore.SIGNAL('triggered()'),self.openCoreTriggered)
       
        self.actionAttach_to_Process = QtGui.QAction('Attach To Process',self)
        self.connect(self.actionAttach_to_Process,QtCore.SIGNAL('triggered()'),self.attachToProcessTriggered)
        
        self.actionOpen_Source_File = QtGui.QAction('Open Source File',self)
       
        self.actionReload_Source_File = QtGui.QAction('Reload Source File',self)
       
        self.actionClose_Source_File = QtGui.QAction('Close Source File',self)

        self.actionExit = QtGui.QAction('Exit',self)
        self.connect(self.actionExit,QtCore.SIGNAL('triggered()'),self.close)
        
############################################################

###########Run Menu Actions#################################
        self.actionRun_Process = QtGui.QAction('Run',self)
        self.connect(self.actionRun_Process,QtCore.SIGNAL('triggered()'),self.actionRun_Process_activated)
        
        self.actionContinue_Process = QtGui.QAction('Continue',self)
        self.connect(self.actionContinue_Process,QtCore.SIGNAL('triggered()'),self.actionContinue_activated)
            
        self.actionKill_Process = QtGui.QAction('Kill',self)
        self.connect(self.actionKill_Process,QtCore.SIGNAL('triggered()'),self.actionKill_Process_activated)
        
        self.actionRestart = QtGui.QAction('Restart',self)
        self.connect(self.actionRestart,QtCore.SIGNAL('triggered()'),self.actionRestart_Process_activated)
############################################################

#################Breakpoint Menu Actions######################
        self.actionSet_Breakpoint = QtGui.QAction('Set Breakpoint',self)
        self.connect(self.actionSet_Breakpoint,QtCore.SIGNAL('triggered()'),self.actionSet_Breakpoint_activated)
        
        self.actionEnable_All_Breakpoints = QtGui.QAction('Enable All',self)
        self.connect(self.actionEnable_All_Breakpoints,QtCore.SIGNAL('triggered()'),self.actionEnable_All_Breakpoints_activated)
        
        self.actionDisable_All_Breakpoints = QtGui.QAction('Disable All',self)
        self.connect(self.actionDisable_All_Breakpoints,QtCore.SIGNAL('triggered()'),self.actionDisable_All_Breakpoints_activated)
        
        self.actionDelete_All_Breakpoints = QtGui.QAction('Delete All',self)
        self.connect(self.actionDelete_All_Breakpoints,QtCore.SIGNAL('triggered()'),self.actionDelete_All_Breakpoints_activated)
        
        self.actionSet_Watchpoint = QtGui.QAction('Set Watchpoint',self)
        self.connect(self.actionSet_Watchpoint,QtCore.SIGNAL('triggered()'),self.actionSet_Watchpoint_activated)
        
        self.actionSet_Catchpoint = QtGui.QAction('Set Catchpoint',self)
        self.connect(self.actionSet_Catchpoint,QtCore.SIGNAL('triggered()'),self.actionSet_Catchpoint_activated)
##############################################################

##############Navigation Menu Actions#########################
        self.actionNext = QtGui.QAction(QtGui.QIcon('next.ico'),'Next',self)
        self.connect(self.actionNext,QtCore.SIGNAL('triggered()'),self.actionNextActivated)
        
        self.actionStep_Out = QtGui.QAction(QtGui.QIcon('step_out.ico'),'Step Out',self)        
        self.connect(self.actionNext,QtCore.SIGNAL('triggered()'),self.actionStepOutActivated)
        
        self.actionStep = QtGui.QAction(QtGui.QIcon('step.ico'),'Step',self)
        self.connect(self.actionStep,QtCore.SIGNAL('triggered()'),self.actionStepActivated)
        
        self.actionStep_into_asm = QtGui.QAction(QtGui.QIcon('step_into_asm.ico'),'Step into asm',self)
        self.connect(self.actionStep_into_asm,QtCore.SIGNAL('triggered()'),self.actionStep_into_asmTriggered)
        
        self.actionStep_over_asm = QtGui.QAction(QtGui.QIcon('step_over_asm.ico'),'Step over asm',self)
        self.connect(self.actionStep_over_asm,QtCore.SIGNAL('triggered()'),self.actionStep_over_asmTriggered)
        
        self.actionJump_to = QtGui.QAction('Jump To',self)
        self.connect(self.actionJump_to,QtCore.SIGNAL('triggered()'),self.actionJumpToTriggered)
##############################################################

###################Expression Menu Actions####################
        self.actionInspect = QtGui.QAction('Inspect',self)
        self.connect(self.actionInspect,QtCore.SIGNAL('triggered()'),self.actionInspectTriggered)
        
        self.actionGlobal_Variables = QtGui.QAction('Global Variables',self)
        self.connect(self.actionGlobal_Variables,QtCore.SIGNAL('triggered()'),self.actionGlobal_VariablesTriggered)       
        
        self.actionLocal_Variables = QtGui.QAction('Local Variables',self)
        self.connect(self.actionLocal_Variables,QtCore.SIGNAL('triggered()'),self.actionLocal_VariablesTriggered)
################################################################

##################View Menu Actions#############################
        self.actionProcess_Terminal = QtGui.QAction('Process Terminal',self)
        self.connect(self.actionProcess_Terminal,QtCore.SIGNAL('triggered()'),self.actionProcess_TerminalTriggered)
        
        self.actionGdb_Console = QtGui.QAction('Gdb Console',self)
        self.connect(self.actionGdb_Console,QtCore.SIGNAL('triggered()'),self.actionGdb_ConsoleTriggered)
        
        self.actionBreakpoints = QtGui.QAction('Breakpoints',self)
        self.connect(self.actionBreakpoints,QtCore.SIGNAL('triggered()'),self.actionBreakpointsTriggered)
        
        self.actionAssembly = QtGui.QAction('Assembly',self)
        self.connect(self.actionAssembly,QtCore.SIGNAL('triggered()'),self.actionAssemblyTriggered)        
                
        self.actionGlobal_Variables_2 = QtGui.QAction('Global Variables',self)
        self.connect(self.actionGlobal_Variables_2,QtCore.SIGNAL('triggered()'),self.actionGlobal_VariablesTriggered)        
        
        self.actionLocal_Variables_2 = QtGui.QAction('Local Variables',self)
        self.connect(self.actionLocal_Variables_2,QtCore.SIGNAL('triggered()'),self.actionLocal_VariablesTriggered)
        
        self.actionRegisters = QtGui.QAction('Registers',self)
        self.connect(self.actionRegisters,QtCore.SIGNAL('triggered()'),self.actionRegisters_triggered)
        
################################################################

#######Appending actions to File Menu###########################
        self.menuFile.addAction(self.actionOpen_Executable_File)
        self.menuFile.addAction(self.actionOpenCoreFile)
        self.menuFile.addAction(self.actionAttach_to_Process)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_Source_File)
        self.menuFile.addAction(self.actionReload_Source_File)
        self.menuFile.addAction(self.actionClose_Source_File)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        
#######Appending actions to Run Menu###########################        
        self.menuRun.addAction(self.actionRun_Process)
        self.menuRun.addAction(self.actionContinue_Process)
        self.menuRun.addAction(self.actionKill_Process)
        self.menuRun.addAction(self.actionRestart)

        self.actionRun_Process.setEnabled(False)
        self.actionContinue_Process.setEnabled(False)
        self.actionKill_Process.setEnabled(False)
        self.actionRestart.setEnabled(False)
        
#######Appending actions to Breakpoints Menu###########################
        self.menuBreakpoints.addAction(self.actionSet_Breakpoint)
        self.menuBreakpoints.addAction(self.actionSet_Watchpoint)
        self.menuBreakpoints.addAction(self.actionSet_Catchpoint)
        self.menuBreakpoints.addSeparator()
        self.menuBreakpoints.addAction(self.actionEnable_All_Breakpoints)
        self.menuBreakpoints.addAction(self.actionDisable_All_Breakpoints)
        self.menuBreakpoints.addAction(self.actionDelete_All_Breakpoints)

        self.actionSet_Breakpoint.setEnabled(False)
        self.actionSet_Watchpoint.setEnabled(False)
        self.actionSet_Catchpoint.setEnabled(False)
        self.actionEnable_All_Breakpoints.setEnabled(False)
        self.actionDisable_All_Breakpoints.setEnabled(False)
        self.actionDelete_All_Breakpoints.setEnabled(False)
        
#######Appending actions to Navigate Menu###########################
        self.menuNavigate.addAction(self.actionNext)
        self.menuNavigate.addAction(self.actionStep)
        self.menuNavigate.addAction(self.actionStep_Out)
        self.menuNavigate.addAction(self.actionStep_into_asm)
        self.menuNavigate.addAction(self.actionStep_over_asm)
        self.menuNavigate.addAction(self.actionJump_to)

        self.actionNext.setEnabled(False)
        self.actionStep.setEnabled(False)
        self.actionStep_Out.setEnabled(False)
        self.actionStep_into_asm.setEnabled(False)
        self.actionStep_over_asm.setEnabled(False)
        self.actionJump_to.setEnabled(False)
        
#######Appending actions to Expression Menu###########################
        self.menuExpression.addAction(self.actionInspect)
        self.menuExpression.addAction(self.actionGlobal_Variables)        
        self.menuExpression.addAction(self.actionLocal_Variables)

        self.actionInspect.setEnabled(False)
        self.actionGlobal_Variables.setEnabled(False)
        self.actionLocal_Variables.setEnabled(False)
        
#######Appending actions to View Menu###########################
        self.menuView.addAction(self.actionProcess_Terminal)
        self.menuView.addAction(self.actionGdb_Console)
        self.menuView.addAction(self.actionBreakpoints)
        self.menuView.addAction(self.actionAssembly)        
        self.menuView.addAction(self.actionGlobal_Variables_2)
        self.menuView.addAction(self.actionLocal_Variables_2)
        self.menuView.addAction(self.actionRegisters)

        self.actionProcess_Terminal.setEnabled(False)
        self.actionGdb_Console.setEnabled(False)
        self.actionBreakpoints.setEnabled(False)
        self.actionAssembly.setEnabled(False)
        self.actionGlobal_Variables_2.setEnabled(False)
        self.actionLocal_Variables_2.setEnabled(False)
        self.actionRegisters.setEnabled(False)
        
#########Appending menus to menu bar###########################
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuBreakpoints.menuAction())
        self.menubar.addAction(self.menuNavigate.menuAction())
        self.menubar.addAction(self.menuExpression.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

###############################################################

##############Toolbar##########################################
        self.toolBar = QtGui.QToolBar(self)
        
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actiontoolOpen_Executable = QtGui.QAction(QtGui.QIcon('load-executable.png'),'Open Executable',self)
        self.toolBar.addAction(self.actiontoolOpen_Executable)

        self.toolBar.addSeparator()

        self.run_runprocess = QtGui.QAction(QtGui.QIcon('run.png'),'Run Process',self)
        self.toolBar.addAction(self.run_runprocess)
        self.run_continue = QtGui.QAction(QtGui.QIcon('continue.png'),'Continue',self)
        self.toolBar.addAction(self.run_continue)
        self.run_restartprocess = QtGui.QAction(QtGui.QIcon('restart.png'),'Restart Process',self)
        self.toolBar.addAction(self.run_restartprocess)
        self.run_stopprocess = QtGui.QAction(QtGui.QIcon('stop.png'),'Stop Process',self)
        self.toolBar.addAction(self.run_stopprocess)

        self.toolBar.addSeparator()
        
        self.toolBar.addAction(self.actionNext)
        self.toolBar.addAction(self.actionStep_Out)
        self.toolBar.addAction(self.actionStep)
        self.toolBar.addAction(self.actionStep_into_asm)
        self.toolBar.addAction(self.actionStep_over_asm)        
        self.toolBar.addSeparator()
        
        self.breakpoints_create = QtGui.QAction(QtGui.QIcon('breakpoint-new.png'),'Create Breakpoint',self)
        self.toolBar.addAction(self.breakpoints_create)        
        self.breakpoints_disable = QtGui.QAction(QtGui.QIcon('breakpoint-disable.png'),'Disable Breakpoint',self)
        self.toolBar.addAction(self.breakpoints_disable)
        self.breakpoints_disableall = QtGui.QAction(QtGui.QIcon('breakpoint-disableall.png'),'Disable All Breakpoints',self)
        self.toolBar.addAction(self.breakpoints_disableall)
        self.breakpoints_enable = QtGui.QAction(QtGui.QIcon('breakpoint-enable.png'),'Enable Breakpoint',self)
        self.toolBar.addAction(self.breakpoints_enable)        
        self.breakpoints_removeall = QtGui.QAction(QtGui.QIcon('breakpoint-removeall.png'),'Remove All Breakpoints',self)
        self.toolBar.addAction(self.breakpoints_removeall)

        self.run_runprocess.setEnabled(False)
        self.run_continue.setEnabled(False)
        self.run_restartprocess.setEnabled(False)
        self.run_stopprocess.setEnabled(False)
        self.breakpoints_create.setEnabled(False)
        self.breakpoints_disable.setEnabled(False)
        self.breakpoints_disableall.setEnabled(False)
        self.breakpoints_enable.setEnabled(False)
        self.breakpoints_removeall.setEnabled(False)
        
#################################################################
        
        self.tabFile.setCurrentIndex(-1)
################gdb Console####################################
        
        self.gdbConsoleDock = QtGui.QDockWidget(self)
        
        self.gdbConsoleEdit = terminal_text_edit.TerminalTextEdit(self.gdbConsoleDock)    
        
        self.gdbConsoleDock.setWidget(self.gdbConsoleEdit)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.gdbConsoleDock)
        self.gdbConsoleDock.setFixedHeight(150)
        
        self.thread = ReadingThread(self.fd,self)
        self.connect(self.thread,QtCore.SIGNAL('readOutput(QString)'),self.readOutput)
        self.connect(self.gdbConsoleEdit,QtCore.SIGNAL('writeCommand(QString)'),self.writeCommand)

        self.thread.start()
        
        os.write(self.fd,'gdb\n')
##############################################################

        self.open_command=""
        self.command = ""
        self.last_created_breakpoint=None
        self.list_breakpoints=[]
        self.full_output=""
        self.inspect_variable=False
        self.inspect_local_vars=False

        self.program_status = 0 #0 for no program, 1 for file loaded and program not running, 2 for program running, 3 for program stopped
        self.program_filepath = ""
        
    def closeEvent(self,event):

        if self.program_status ==2 or self.program_status ==3:
            msg = QtGui.QMessageBox("A program is currently being debugged. Are you sure you want to quit?", QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
            if msg == QtGui.QMessageBox.Yes:
                event.accept()            
        
    def readOutput(self,string):

        self.full_output += str(string)
        #print 'self.full_output'+self.full_output+'llllllll'
        
        if self.full_output.find("(gdb)")!=-1 or self.full_output.find("y or ")!=-1:
            self.readFullOutput(self.full_output)
            self.full_output="" 
        elif self.full_output.find('---Type <return> to continue')!=-1:
            
            os.write(self.fd,'\n\n')       
        
    def readFullOutput(self,string):

        string =str(string)
        
        if string.find('(no debugging symbols found)')!=-1:
            ask = QtGui.QMessageBox.information(self,'Debugger','No debugging symbols found in current file. Recompile the source file with gcc using -g flag.',QtGui.QMessageBox.Ok)
        
        if self.open_command.find("attach")!=-1:
            _tuple= re.findall("warning: process ([0-9]*) is already traced by process ([0-9]*)",string)
            try:
                ask = QtGui.QMessageBox.information("Warning: Process %d is already traced by process %d" %(_tuple[0],_tuple[1]),QtGui.QMessageBox.Ok)
            except IndexError:
                pass
                
        if self.command == 'open-all-source-files' and string.find('Source files for which symbols will be read in on demand')!=-1:            
            found = False
            last_pos=0            
            for searchiter in re.finditer(r'(?<=/)+.+?(?=,)',string):
                found = True            
                last_pos=searchiter.end()-1
                filename=searchiter.group()
                filename='/'+filename
                filename_exists=False
                filename=filename.replace('\r','')                
                for code_widget in self.list_code_widget:
                    if filename==code_widget.filename:                        
                        filename_exists=True
                for _tuple in self.list_file_old_new:
                    if filename==_tuple[0]:
                        filename_exists=True
                if filename_exists==True:
                    continue
                
                s_edit = source_editor.CodeWidget(self)
                
                if s_edit.open_file(filename)==-1:
                    ask = QtGui.QMessageBox.information(self,'Debugger','Cannot find %s. Do you know where the file is?'%(filename),QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
                    if ask == QtGui.QMessageBox.Yes:
                        filename_new = str(QtGui.QFileDialog.getOpenFileName(self,'Open File'))
                        if filename_new!="":
                            self.list_code_widget.append(s_edit)
                            self.tabFile.addTab(s_edit,filename[filename.rfind('/')+1:])
                            self.list_file_old_new.append((filename,filename_new))
                            self.list_code_widget[len(self.list_code_widget)-1].open_file(filename_new)
                else:
                    self.list_code_widget.append(s_edit)
                    self.tabFile.addTab(s_edit,filename[filename.rfind('/')+1:])

                self.connect(s_edit,QtCore.SIGNAL('setBreakpoint(int)'),self.codeWidgetSetBreakpoint)
                self.connect(s_edit,QtCore.SIGNAL('breakpointStateChanged(int,int)'),self.codeWidgetBreakpointStateChanged)

            r = re.compile(r',+.+(?!,)')
            last_iter = r.search(string,last_pos)
            if last_iter!=None:                
                found = True
                filename=last_iter.group()
                filename=filename.replace(',','')
                filename=filename.strip()
                if filename=="":
                    return
                filename='/'+filename
                filename_exists=False
                filename=filename.replace('\r','')
                
                for code_widget in self.list_code_widget:
                    if filename==code_widget.filename:                        
                        filename_exists=True
                for _tuple in self.list_file_old_new:
                    if filename==_tuple[0]:
                        filename_exists=True
                if filename_exists==True:
                    return
                
                s_edit = source_editor.CodeWidget(self)
                
                if s_edit.open_file(filename)==-1:
                    ask = QtGui.QMessageBox.information(self,'Debugger','Cannot find %s. Do you know where the file is?'%(filename),QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
                    if ask == QtGui.QMessageBox.Yes:
                        filename_new = str(QtGui.QFileDialog.getOpenFileName(self,'Open File'))
                        if filename_new!="":
                            self.list_code_widget.append(s_edit)
                            self.tabFile.addTab(s_edit,filename[filename.rfind('/')+1:])
                            self.list_file_old_new.append((filename,filename_new))
                            self.list_code_widget[len(self.list_code_widget)-1].open_file(filename_new)
                else:
                    self.list_code_widget.append(s_edit)
                    self.tabFile.addTab(s_edit,filename[filename.rfind('/')+1:])

                self.connect(s_edit,QtCore.SIGNAL('setBreakpoint(int)'),self.codeWidgetSetBreakpoint)
                self.connect(s_edit,QtCore.SIGNAL('breakpointStateChanged(int,int)'),self.codeWidgetBreakpointStateChanged)
            
            if found==False:

                filename = re.findall(r'/+.+',string)[0]
                filename=filename.strip()
                if filename=="":
                    return
                filename_exists=False
                filename=filename.replace('\r','')
                
                for code_widget in self.list_code_widget:
                    if filename==code_widget.filename:                        
                        filename_exists=True
                for _tuple in self.list_file_old_new:
                    if filename==_tuple[0]:
                        filename_exists=True
                if filename_exists==True:
                    return
                
                s_edit = source_editor.CodeWidget(self)
                
                if s_edit.open_file(filename)==-1:
                    ask = QtGui.QMessageBox.information(self,'Debugger','Cannot find %s. Do you know where the file is?'%(filename),QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
                    if ask == QtGui.QMessageBox.Yes:
                        filename_new = str(QtGui.QFileDialog.getOpenFileName(self,'Open File'))
                        if filename_new!="":
                            self.list_code_widget.append(s_edit)
                            self.tabFile.addTab(s_edit,filename[filename.rfind('/')+1:])
                            self.list_file_old_new.append((filename,filename_new))
                            self.list_code_widget[len(self.list_code_widget)-1].open_file(filename_new)
                else:
                    self.list_code_widget.append(s_edit)
                    self.tabFile.addTab(s_edit,filename[filename.rfind('/')+1:])

                self.connect(s_edit,QtCore.SIGNAL('setBreakpoint(int)'),self.codeWidgetSetBreakpoint)
                self.connect(s_edit,QtCore.SIGNAL('breakpointStateChanged(int,int)'),self.codeWidgetBreakpointStateChanged)
                
        if self.command=='stop\n':
            if string.find('killed')!=-1:
                ask=QtGui.QMessageBox.information('Inferior Process Killed',QtGui.QMessageBox.Ok)
                self.direct_to_inferior_terminal=False

        if self.direct_to_inferior_terminal==True:
            self.inferior_terminal_dialog.terminal_text_edit.appendOutput(string)

        if string.find('Inferior')!=-1 and string.find('exited normally]')!=-1:
            ask = QtGui.QMessageBox.information(self,'Debugger','Inferior Process exited normally',QtGui.QMessageBox.Ok)
            self.direct_to_inferior_terminal=False
            self.program_status = 1

        if "set_break_at_" in self.command:
            if string.find('y or [n]')!=-1:
                return
            b_id = re.findall(r'Breakpoint\s*([0-9]+)',string)[0]
            self.last_created_breakpoint.set_id(b_id)
            self.list_breakpoints.append(self.last_created_breakpoint)
            if "file_line" in self.command:
                filename = self.last_created_breakpoint.filename
                for i in range(self.tabFile.count()):
                    if filename==str(self.tabFile.tabText(i)):                       
                        self.list_code_widget[i].addBreakpoint(self.last_created_breakpoint)
                        break
                    
        if self.command=='inspect-variable':

            val=re.findall(r'\$[0-9]+\s=+.+',string)            
            if val!=[]:
                val = val[0]
            else:
                val=""
            
            val_type=re.findall(r'type\s=\s+.+',string)            
            if val_type!=[]:
                val_type=val_type[0]
            else:
                val_type=""
                
            self.inspect_exp_dlg.setExpData(val,val_type)
        else:
            if 'whatis ' in self.gdbConsoleEdit.command:
                if self.inspect_variable==True:
                    command= str(self.gdbConsoleEdit.command)
                    val_name = command[command.find(' ')+1:]
                    val_name = val_name.strip()
                    val_type = re.findall(r'type\s=\s+.+',string)
                    if val_type!=[]:
                        val_type=val_type[0]
                    else:
                        val_type=""
                    self.setValType(self.parent_var,val_name,val_type)
                    
                elif self.inspect_local_vars==True:
                    command= str(self.gdbConsoleEdit.command)
                    val_name = command[command.find(' ')+1:]
                    val_name = val_name.strip()
                    val_type = re.findall(r'type\s=\s+.+',string)
                    if val_type!=[]:
                        val_type=val_type[0]
                    else:
                        val_type=""
                    
                    for var in self.list_local_vars:
                        self.setLocalValType(var,val_name,val_type)
                
        if 'set_watchpoint' in self.command:
            
            if string.find('y or [n]')!=-1:
                return
            b_id = re.findall(r'Hardware\swatchpoint\s*([0-9]+)',string)[0]
            self.last_created_breakpoint.set_id(b_id)
            self.list_breakpoints.append(self.last_created_breakpoint)           

        if 'catch' in self.command:

            if string.find('y or [n]')!=-1:
                return
            b_id = re.findall(r'Catchpoint\s*([0-9]+)',string)[0]
            self.last_created_breakpoint.set_id(b_id)
            self.list_breakpoints.append(self.last_created_breakpoint)
        
        if 'info_locals' in self.command:
            self.inspect_locals(string.replace('(gdb)',""))
            
        if 'info all-registers'==self.command:
            self.registers_dlg.setString(string)            
        if 'disas' in self.command:
            self.assembly_dlg.setText(string)
        if re.findall(r'Breakpoint\s*[0-9]*,.+at+.+:[0-9]+',string)!=[]:
            matched_string = re.findall(r'Breakpoint\s*[0-9]*,.+at+.+:[0-9]+',string)[0]
            filename = matched_string[matched_string.find('at ')+3:matched_string.find(':')]
            filename = filename.strip()
            line_number = matched_string[matched_string.find(':')+1:]            
            line_number = int(line_number)
            for code_widget in self.list_code_widget:
                if code_widget.filepath == filename:
                    code_widget.setLinePointerAtLine(line_number)
            self.program_status = 3
            
        if re.findall(r'Program received signal\s+.+.+at+.+:[0-9]+',string,re.DOTALL):
            matched_string =re.findall(r'Program received signal\s+.+.+at+.+:[0-9]+',string,re.DOTALL)[0]
            self.direct_to_inferior_terminal=False
            signal = string[string.find('signal')+len('string')+1:string.find('.',string.find('signal'))]
            signal = signal.strip()
            ask = QtGui.QMessageBox.information(self,'Debugger','Program recieved '+signal,QtGui.QMessageBox.Ok)
            filename = matched_string[matched_string.find('at ')+3:matched_string.find(':')]
            filename = filename.strip()
            line_number = matched_string[matched_string.find(':')+1:]            
            line_number = int(line_number)
            for code_widget in self.list_code_widget:
                if code_widget.filepath == filename:
                    code_widget.setLinePointerAtLine(line_number)
            self.program_status = 3
                    
        if 'info variables' in self.command:

            string1 = string[:string.find('Non-debugging symbols:')]
            string1 = string1.replace('All defined variables:','')
            for s in re.findall(r'.+',string1):
                if s.find('File')!=-1 and s.find(':')!=-1:
                    continue
                
                s = s.replace(';','')
                var_name = s[s.rfind(' ')+1:]
                var_type = s.replace(var_name,'')
                var_name = var_name.strip()
                var_type = var_type.strip()
                self.list_local_vars.append(VariableTree(var_name,"",var_type,None))
        
            self.generateInspectGlobal()

        elif 'print ' in self.command:

            command = str(self.gdbConsoleEdit.command)
            var_name = command[command.find(' ')+1:]
            var_name = var_name.strip()
            val=re.findall(r'\$[0-9]+\s=+.+',string)            
            if val!=[]:
                val = val[0]
                self.setGlobalLocalVarVal(var_name,val)
            
        self.gdbConsoleEdit.appendOutput(string)

    def setGlobalLocalVarVal(self,var_name,val):

        val = val[val.find('=')+1:]
        val = val.strip()
        for var in self.list_local_vars:
            if var.scope_name == var_name:
                var.val = val

        allVarFilled=True
        for var in self.list_local_vars:
            if var.val=="":
                allVarFilled=False

        if allVarFilled==True:
            for var in self.list_local_vars:
                if var.name!="" and var.val!="" and var.type!="":
                    self.global_vars_dlg.setExpData(var.name,var.val,var.type)                
            
    def generateInspectGlobal(self):
        
        for var in self.list_local_vars:

            self.command = 'print '+var.name
            self.gdbConsoleEdit.runCommand(self.command)
            
    def setValType(self,var_tree,val_name,val_type):

        if var_tree != None and var_tree.scope_name==val_name:
            var_tree.type=val_type            
            return

        for var in var_tree.list_variables:
            self.setValType(var,val_name,val_type)
            if self.isAllVarType(self.parent_var)==True:
                self.inspect_exp_dlg.setStructData(self.parent_var)
            
    def isAllVarType(self,var_tree):

        if var_tree.type=="":
            return False        

        for var in var_tree.list_variables:
            if self.isAllVarType(var)==False:
                return False

        return True

    def setLocalValType(self,var_tree,var_name,var_type):
        
        if var_tree != None and var_tree.scope_name==var_name:            
            var_tree.type=var_type
            if self.isAllLocalVarHasType()==True:                
                for var in self.list_local_vars:
                    if var.list_variables==[]:
                        self.local_vars_dlg.setExpData(var.name,var.val,var.type)
                    else:
                        self.local_vars_dlg.setStructData(var)
            return

        for var in var_tree.list_variables:
            self.setLocalValType(var,var_name,var_type)
            all_true=True       

    def isAllLocalVarHasType(self):

        for var in self.list_local_vars:
            if self.isAllVarType(var)==False:
                return False

        return True    
    
    def writeCommand(self,string):
        
        os.write(self.fd,str(string))

    def openExecutableTriggered(self):

        self.open_exec_dialog = open_executable.OpenExecutableDialog(self)
        self.connect(self.open_exec_dialog,QtCore.SIGNAL('finished(int)'),self.open_exec_dialog_finished)
        self.open_exec_dialog.exec_()

    def open_exec_dialog_finished(self,result):

        if result==1:   
            self.open_command = self.command = 'file ' + str(self.open_exec_dialog.entryExecutable.text())
            self.gdbConsoleEdit.runCommand(self.command+'\n')
            import time
            time.sleep(0.001)
            
            if str(self.open_exec_dialog.entryArg.text())!="":
                self.command = 'set args '+str(self.open_exec_dialog.entryArg.text())
                self.gdbConsoleEdit.runCommand(self.command+'\n')
            time.sleep(0.001)
            
            if str(self.open_exec_dialog.entryWorking.text())!="":
                self.gdbConsoleEdit.runCommand('cd '+str(self.open_exec_dialog.entryWorking.text())+'\n')                
            time.sleep(0.001)
            
            for i in range(self.open_exec_dialog.envVarView.rowCount()):
                self.command = 'set env '
                if self.open_exec_dialog.envVarView.item(i,0)==None or str(self.open_exec_dialog.envVarView.item(i,0).text())=="":
                    continue
                self.command += str(self.open_exec_dialog.envVarView.item(i,0).text())+' = '
                self.command += str(self.open_exec_dialog.envVarView.item(i,1).text())+'\n'
                self.gdbConsoleEdit.runCommand(self.command)
                time.sleep(0.001)

            time.sleep(0.01)
            self.open_exec_source_files()

            self.run_runprocess.setEnabled(True)
            self.run_continue.setEnabled(True)
            self.run_restartprocess.setEnabled(True)
            self.run_stopprocess.setEnabled(True)
            self.breakpoints_create.setEnabled(True)
            self.breakpoints_disable.setEnabled(True)
            self.breakpoints_disableall.setEnabled(True)
            self.breakpoints_enable.setEnabled(True)
            self.breakpoints_removeall.setEnabled(True)
            self.actionRun_Process.setEnabled(True)
            self.actionContinue_Process.setEnabled(True)
            self.actionKill_Process.setEnabled(True)
            self.actionRestart.setEnabled(True)
            self.actionSet_Breakpoint.setEnabled(True)
            self.actionSet_Watchpoint.setEnabled(True)
            self.actionSet_Catchpoint.setEnabled(True)
            self.actionEnable_All_Breakpoints.setEnabled(True)
            self.actionDisable_All_Breakpoints.setEnabled(True)
            self.actionDelete_All_Breakpoints.setEnabled(True)
            self.actionNext.setEnabled(True)
            self.actionStep.setEnabled(True)
            self.actionStep_Out.setEnabled(True)
            self.actionStep_into_asm.setEnabled(True)
            self.actionStep_over_asm.setEnabled(True)
            self.actionJump_to.setEnabled(True)
            self.actionInspect.setEnabled(True)
            self.actionGlobal_Variables.setEnabled(True)
            self.actionLocal_Variables.setEnabled(True)
            self.actionProcess_Terminal.setEnabled(True)
            self.actionGdb_Console.setEnabled(True)
            self.actionBreakpoints.setEnabled(True)
            self.actionAssembly.setEnabled(True)
            self.actionGlobal_Variables_2.setEnabled(True)
            self.actionLocal_Variables_2.setEnabled(True)
            self.actionRegisters.setEnabled(True)
        
    def openCoreTriggered(self):
        
        self.open_core_file_dialog = open_core_file.OpenCoreFileDialog(self)
        self.connect(self.open_core_file_dialog,QtCore.SIGNAL('finished(int)'),self.open_core_file_dialog_finished)
        self.open_core_file_dialog.exec_()

    def attachToProcessTriggered(self):

        self.attach_process_dialog = attach_process.AttachProcessDialog(self)
        self.connect(self.attach_process_dialog,QtCore.SIGNAL('finished(int)'),self.attach_process_dialog_finished)
        self.attach_process_dialog.exec_()

    def attach_process_dialog_finished(self,result):
        
        if result == 1:
            self.open_command = self.command = 'attach '+str(self.attach_process_dialog.lineEditPid.text())
            self.gdbConsoleEdit.runCommand(self.command+'\n')
            self.open_exec_source_files()
            
    def open_core_file_dialog_finished(self,result):

        if result==1:
            self.open_command = self.command = 'exec-file ' + str(self.open_exec_dialog.lineEditExec.text())
            self.gdbConsoleEdit.runCommand(command+'\n')

            self.command = 'core-file ' + str(self.open_core_file_dialog.lineEditCore.text())
            self.gdbConsoleEdit.runCommand(command+'\n')

    def open_exec_source_files(self):
       
        if self.open_command.find('file')!=-1 or self.open_command.find('attach')!=-1 or self.open_command.find('exec-file')!=-1:
       
            self.command = 'open-all-source-files'
            self.gdbConsoleEdit.runCommand('info sources\n')

    def actionNextActivated(self):

        self.command='next\n'
        self.gdbConsoleEdit.runCommand(self.command)
        
    def actionStepActivated(self):

        self.command='step\n'
        self.gdbConsoleEdit.runCommand(self.command)

    def actionStepOutActivated(self):

        self.command = 'finish\n'
        self.gdbConsoleEdit.runCommand(self.command)

    def actionStep_into_asmTriggered(self):

        self.command = 'ni\n'
        self.gdbConsoleEdit.runCommand(self.command)

    def actionStep_over_asmTriggered(self):

        self.command = 'si\n'
        self.gdbConsoleEdit.runCommand(self.command)

    def actionJumpToTriggered(self):

        self.jump_to_dialog = jump_to_dialog.JumpToDialog(self)
        self.connect(self.jump_to_dialog,QtCore.SIGNAL('finished(int)'),self.jump_to_dialog_finished)
        self.jump_to_dialog.exec_()
        
    def jump_to_dialog_finished(self,result):

        if result == 1:
            jump_to_dlg = self.jump_to_dialog
            if jump_to_dlg.rbFunction.isChecked()==True:
                self.command='jump '+str(jump_to_dlg.lineEditFunc.text())
            if jump_to_dlg.rbAddress.isChecked()==True:
                self.command='jump '+str(jump_to_dlg.lineEditAddress.text())
            if jump_to_dlg.rbSourceFile.isChecked()==True:
                self.command='jump '+str(jump_to_dlg.lineEditFile.text())+':'+str(jump_to_dlg.lineEditLine.text())

            self.gdbConsoleEdit.runCommand(self.command)
                
    def actionRun_Process_activated(self):

        self.gdbConsoleEdit.runCommand('run\n')
        self.inferior_terminal_dialog.show_dialog()
        self.direct_to_inferior_terminal=True            
        self.program_status = 2
        
    def actionContinue_activated(self):

        self.gdbConsoleEdit.runCommand('cont\n')
        self.inferior_terminal_dialog.show_dialog()
        self.direct_to_inferior_terminal=True
        self.program_status = 2
        
    def actionKill_Process_activated(self):

        self.command='stop\n'
        self.gdbConsoleEdit.runCommand('kill\n')
        ask = QtGui.QMessageBox.question("Do you want to kill the process?",QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if ask  == QtGui.QMessageBox.Yes:
            self.gdbConsoleEdit.runCommand('y\n')
        else:
            self.gdbConsoleEdit.runCommand('n\n')
        self.terminal_text_edit.close()
        self.direct_to_inferior_terminal=False
        self.program_status = 1
        
    def actionRestart_Process_activated(self):

        self.command='run\n'
        self.gdbConsoleEdit.runCommand('run\n')
        ask = QtGui.QMessageBox.question("Do you want to restart the process?",QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if ask  == QtGui.QMessageBox.Yes:
            self.gdbConsoleEdit.runCommand('y\n')
        else:
            self.gdbConsoleEdit.runCommand('n\n')
        self.terminal_text_edit.close()
        self.direct_to_inferior_terminal=True
        self.inferior_terminal_dialog.show_dialog()
        self.program_status = 2
        
    def actionSet_Breakpoint_activated(self):

        self.set_breakpoint_dialog = set_breakpoint.SetBreakpointDialog(self)
        self.connect(self.set_breakpoint_dialog,QtCore.SIGNAL('finished(int)'),self.set_breakpoint_dialog_finished)
        self.set_breakpoint_dialog.exec_()

    def set_breakpoint_dialog_finished(self, result):

        if result==1:
            command2=""
            if self.set_breakpoint_dialog.rbFunction.isChecked()==True:
                self.command = 'break ' + str(self.set_breakpoint_dialog.lineEditFunction.text()) + '\n'
                command2="set_break_at_function"
                self.last_created_breakpoint = FunctionBreakpoint(1,str(self.set_breakpoint_dialog.lineEditFunction.text()))
            if self.set_breakpoint_dialog.rbSourceFile.isChecked()==True:
                self.command = 'break ' + str(self.set_breakpoint_dialog.lineEditFileName.text()) +':'+ str(self.set_breakpoint_dialog.lineEditLineNumber.text())+'\n'
                command2="set_break_at_file_line"
                self.last_created_breakpoint=LineBreakpoint(1,str(self.set_breakpoint_dialog.lineEditLineNumber.text()),str(self.set_breakpoint_dialog.lineEditFileName.text()))
            if self.set_breakpoint_dialog.rbAddress.isChecked()==True:
                self.command = 'break *' + str(self.set_breakpoint_dialog.lineEditAddress.text()) + '\n'
                command2="set_break_at_address"
                self.last_created_breakpoint = AddressBreakpoint(1,str(self.set_breakpoint_dialog.lineEditAddress.text()))
            
            self.gdbConsoleEdit.runCommand(self.command)
            self.command=command2
            
    def actionEnable_All_Breakpoints_activated(self):
        
        for b in self.list_breakpoints:
            b.state=1
            
        for code_widget in self.list_code_widget:
            code_widget.enableAllBreakpoints()
            
        self.gdbConsoleEdit.runCommand('enable')
            
    def actionDisable_All_Breakpoints_activated(self):

        for b in self.list_breakpoints:
            b.state=0

        for code_widget in self.list_code_widget:
            code_widget.disableAllBreakpoints()
            
        self.gdbConsoleEdit.runCommand('disable')
        
    def actionDelete_All_Breakpoints_activated(self):

        self.list_breakpoints=[]
        for code_widget in self.list_code_widget:
            code_widget.list_breakpoints=[]
            
    def actionSet_Watchpoint_activated(self):

        self.setWatchpointDialog = set_watchpoint_dialog.SetWatchpointDialog(self)
        self.inspect_exp_dlg=self.setWatchpointDialog
        self.connect(self.inspect_exp_dlg,QtCore.SIGNAL('inspectVariable(QString)'),self.inspect_dlg_inspect_var)
        self.connect(self.inspect_exp_dlg,QtCore.SIGNAL('inspectStruct(QString)'),self.inspect_dlg_inspect_struct)
        self.connect(self.setWatchpointDialog,QtCore.SIGNAL('setWatchpoint()'),self.setWatchpointDialog_set)
        self.setWatchpointDialog.exec_()    
    
    def setWatchpointDialog_set(self):

        currentItem = self.setWatchpointDialog.treeWidget.currentItem()
        var_name = currentItem.text(0)
        var = self.parent_var.get_var_from_name(var_name)
        if var==None:
            QtGui.QMessageBox.information(self,'Cannot find the given variable',QtGui.QMessageBox.Ok)
            return
        
        watchpointType = ""
        watchpointType1=""

        if self.setWatchpointDialog.cbRead.isChecked()==True:
            watchpointType="r"
            watchpointType1="Read"
        if self.setWatchpointDialog.cbWrite.isChecked()==True:
            watchpointType=""
            watchpointType1="Write"
        if self.setWatchpointDialog.cbWrite.isChecked()==True and self.setWatchpointDialog.cbRead.isChecked()==True:
            watchpointType="a"
            watchpointType1="Read/Write"

        self.command = watchpointType + 'watch ' + var.scope_name
        self.gdbConsoleEdit.runCommand(self.command)
        self.command = "set_watchpoint"
        self.last_created_breakpoint = Watchpoint(str(self.inspect_exp_dlg.lineEditExp.text()),1,watchpointType1)
        
    def actionSet_Catchpoint_activated(self):

        self.setCatchpointDialog = set_catchpoint_dialog.SetCatchpointDialog(self)
        self.connect(self.setCatchpointDialog,QtCore.SIGNAL('finished(int)'),self.setCatchpointDialogFinished)
        self.setCatchpointDialog.exec_()

    def setCatchpointDialogFinished(self, state):

        if state==1:
            if self.setCatchpointDialog.rbThrow.isChecked()==True:
                self.command = "catch throw"
                self.last_created_breakpoint = CatchpointThrow()
                
            if self.setCatchpointDialog.rbCatch.isChecked()==True:
                self.command = "catch catch"
                self.last_created_breakpoint = CatchpointThrow()
                
            if self.setCatchpointDialog.rbExec.isChecked()==True:
                self.command = "catch exec"
                self.last_created_breakpoint = CatchpointCatch()
                
            if self.setCatchpointDialog.rbSystemCall.isChecked()==True:
                self.command = "catch syscall " + str(self.setCatchpointDialog.lineEditSysCall.text())
                self.last_created_breakpoint = CatchpointSysCall(str(self.setCatchpointDialog.lineEditSysCall.text()))
                
            self.gdbConsoleEdit.runCommand(self.command)            
            
    def codeWidgetSetBreakpoint(self,line):

        currentIndex =self.tabFile.currentIndex()
        filename = str(self.tabFile.tabText(currentIndex))
        for _tuple in self.list_file_old_new:
            if filename==_tuple[1]:
                filename=_tuple[0]
                
        self.command = 'break ' + filename +':'+ str(line) +'\n'
        command2="set_break_at_file_line"
        self.last_created_breakpoint=LineBreakpoint(1,str(line),filename)
        self.gdbConsoleEdit.runCommand(self.command)
        self.command=command2

    def codeWidgetBreakpointStateChanged(self,line_number,state):
        
        currentIndex = self.tabFile.currentIndex()
        code_widget = self.list_code_widget[currentIndex]
        for breakpoint in self.list_breakpoints:            
            if breakpoint.filename==str(self.tabFile.tabText(currentIndex)):
                if int(breakpoint.line)==line_number:                
                    breakpoint.state=state
                    if state==1:
                        self.command = 'enable '+ breakpoint.id
                    else:
                        self.command = 'disable '+ breakpoint.id
                    self.gdbConsoleEdit.runCommand(self.command + '\n')
                    break
            
    def actionInspectTriggered(self):

        self.inspect_exp_dlg = inspect_expression_dialog.InspectExpressionDialog(self)
        self.connect(self.inspect_exp_dlg,QtCore.SIGNAL('inspectVariable(QString)'),self.inspect_dlg_inspect_var)
        self.connect(self.inspect_exp_dlg,QtCore.SIGNAL('inspectStruct(QString)'),self.inspect_dlg_inspect_struct)
        self.inspect_variable=True
        self.inspect_local_vars=False
        self.inspect_exp_dlg.exec_()
        
    def inspect_dlg_inspect_var(self, var):

        var = str(var)
        self.command = 'print '+ var +'\n'
        self.gdbConsoleEdit.runCommand(self.command)
        self.command = 'whatis ' + var + '\n'
        self.gdbConsoleEdit.runCommand(self.command)
        self.command='inspect-variable'
        self.list_commands=[]
        self.parent_var = None

    def inspect_struct(self,var,parent):

        match_str = str(var)
                    
        match_str = match_str[match_str.find('{')+1:]
        match_str = match_str[:match_str.rfind('}')]
        match_str1=""
        try:            
            match_str1 = re.findall(r'\{+.+?\}',match_str)[0]
            count = match_str1.count('{')-match_str1.count('}')
            i=0
            while count >0:
                match_str2 = re.findall(r'(?<=\})+.+(?=\})',var)[i]+'}'
                match_str1 += match_str2
                count = match_str1.count('{')-match_str1.count('}')
                i+=1
            match_str=match_str.replace(match_str1,"")
        except IndexError:
            pass
        
        for splitted_str in match_str.split(','):
            name = splitted_str[:splitted_str.find('=')]
            name = name.strip()

            val = splitted_str[splitted_str.find('=')+1:]
            val = val.strip()            
            if val == "=" or val=="":
                val = match_str1
                new_parent = VariableTree(name,val,"",parent)
                parent.list_variables.append(new_parent)                
                self.inspect_struct(match_str1,new_parent)
            else:
                parent.list_variables.append(VariableTree(name,val,"",parent))        

    def inspect_locals(self,string):

        for val in re.findall(r'.+',string.replace('(gdb)',"")):

            if val.strip()=="":
                continue
            val_val = val[val.find('=')+1:]
            val_val = val_val.strip()
            val_name = val[:val.find('=')]
            val_name = val_name.strip()
            parent=VariableTree(val_name,val_val,"",None)
            self.list_local_vars.append(parent)
            if val_val.find('{')!=-1:
                self.inspect_struct(val_val,parent)

        for var in self.list_local_vars:
            
            self.produce_whatis_local_vars(var)

    def produce_whatis_local_vars(self,var):

        if var.scope_name.strip()!="":
            self.command = 'whatis ' + var.scope_name+'\n'
            self.gdbConsoleEdit.runCommand(self.command)
            
        for var1 in var.list_variables:
            self.produce_whatis_local_vars(var1)
    
    def inspect_dlg_inspect_struct(self, var):

        self.parent_var = VariableTree(self.inspect_exp_dlg.lineEditExp.text(),self.inspect_exp_dlg.exp_val,self.inspect_exp_dlg.exp_type,None)
        self.inspect_struct(var,self.parent_var)
        self.current_vartree=self.parent_var
        self.runWhatIsCommands(self.parent_var)
        
    def runWhatIsCommands(self,varTree):

        self.command = 'inspect-struct '+varTree.scope_name
        self.gdbConsoleEdit.runCommand('whatis ' + varTree.scope_name)       
        for var in varTree.list_variables:
            self.runWhatIsCommands(var)

    def actionLocal_VariablesTriggered(self):

        self.local_vars_dlg = local_vars_dlg.LocalVarsDialog(self)
        self.command = 'info locals'
        self.gdbConsoleEdit.runCommand(self.command+'\n')
        self.command = 'info_locals'        
        self.list_local_vars=[]
        self.inspect_variable=False
        self.inspect_local_vars=True
        self.local_vars_dlg.exec_()
        
    def local_vars_dlg_inspect_struct(self, var):

        self.list_local_vars.append(self.current_vartree)

    def actionGlobal_VariablesTriggered(self):

        self.global_vars_dlg= global_vars_dlg.GlobalVarsDialog(self)
        self.list_global_vars = []
        self.command = 'info variables'
        self.gdbConsoleEdit.runCommand(self.command)
        self.list_local_vars=[]        
        self.global_vars_dlg.exec_()
        
    def actionRegisters_triggered(self):

        self.registers_dlg = registers_dialog.RegistersDialog(self)
        self.command='info all-registers'
        self.gdbConsoleEdit.runCommand(self.command)
        self.registers_dlg.exec_()        

    def actionAssemblyTriggered(self):

        self.assembly_dlg = assembly_dialog.AssemblyDialog(self)
        self.command = 'disas\n'
        self.gdbConsoleEdit.runCommand(self.command)
        self.assembly_dlg.exec_()

    def actionBreakpointsTriggered(self):

        self.breakpoints_dlg = breakpoints_dialog.BreakpointsDialog(self)
        self.breakpoints_dlg.exec_()

    def actionProcess_TerminalTriggered(self):

        self.inferior_terminal_dialog.setVisible(not self.inferior_terminal_dialog.isVisible())

    def actionGdb_ConsoleTriggered(self):

        self.gdbConsoleEdit.setVisible(not self.gdbConsoleEdit.isVisible())
        
app = QtGui.QApplication(sys.argv)
nt = MainWindow()
nt.show()
app.exec_()
