
VERSION = "SAV v1.1"

import sys, time, threading, cv2
try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import QTimer, QPoint, QRect, pyqtSignal, QThread,QDateTime
    from PyQt5.QtWidgets import QMenu,QSizePolicy, QApplication, QMainWindow, QTextEdit, QLabel, QComboBox, QSlider, QMessageBox, QCheckBox,QDialog,QLineEdit, QDialogButtonBox,QPushButton
    from PyQt5.QtWidgets import QTabWidget,QTreeWidgetItem, QTreeWidget,QWidget, QAction, QVBoxLayout, QHBoxLayout, QDockWidget,QFrame
    from PyQt5.QtGui import QFont, QPainter, QImage, QPixmap,QTextCursor,QStandardItemModel,QStandardItem, QPalette, QIcon
else:
    from PyQt4.QtCore import Qt, QPoint, QRect, pyqtSignal, QTimer, QPoint
    from PyQt4.QtGui import QMenu,QApplication, QMainWindow, QTextEdit, QLabel, QComboBox,QSlider, QMessageBox
    from PyQt4.QtGui import QTabWidget, QTreeWidgetItem, QTreeWidget,QWidget, QAction, QVBoxLayout, QHBoxLayout,QDockWidget
    from PyQt4.QtGui import QFont, QPainter, QImage, QPixmap, QTextCursor,QStandardItemModel, QStandardItem,QPalette, QIcon
try:
    import Queue as Queue
except:
    import queue as Queue
    
import qtmodern.styles
import qtmodern.windows
import os
import glob
from client import client
import json

from topic import settingsDlg as connexionSettings, topic 
 
TEXT_FONT   = QFont("Courier", 10)

 
def validateJSON(jsonData):
    try :
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

class MyWindow(QMainWindow):
    text_update = pyqtSignal(str)

    # Create main window
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
     
    
        MainLayout = QVBoxLayout()
        self.vlayout        = QVBoxLayout()        # Window layout
        frame = QFrame()
        frame.setLayout(self.vlayout )
        self.setCentralWidget(frame)
     
        #===========================
        # tabs
        #===========================
        
        self.tabs = QTabWidget()
        self.vlayout.addWidget(self.tabs )
        #======================================
        # Menu
        #======================================
        mainMenu = self.menuBar()      # Menu bar
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(exitAction)

   
        CamAction  = QAction('&Connexion Settings', self)
        CamAction.triggered.connect(self.connexionSettings)
        connexionAction = QAction('&Start connexion', self)
        connexionAction.triggered.connect(self.startConnexion)
        ConnexionMenu =  mainMenu.addMenu('&Connexion')
 
        ConnexionMenu.addAction(CamAction)
        ConnexionMenu.addAction(connexionAction)                        
        '''
 
        
        showCommandsAction  = QAction('&commands', self)
        showCommandsAction.triggered.connect(self.ShowCommandsWidget)
        showCommandsAction.setCheckable(True)
        showCommandsAction.setChecked(False)
        
        self.processing.addAction(detectionAction)
        self.processing.addAction(anprAction)
        self.processing.addAction(self.showControlAction)
        self.processing.addAction(self.showCommandsAction)
        '''
        #==================================
        # dock widget
        #==================================
        commands          = QVBoxLayout()
        #------> tree des clients
        self.tree  = QTreeWidget()
        self.tree.setColumnCount(2)
        head = []
        head.append("id")
        head.append("type")
        self.tree.setHeaderLabels(head)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)
        
        commands.addWidget(self.tree )
        
        self.treeClients = QTreeWidgetItem( self.tree)
        self.treeClients.setText(0,'network');
        
        #------> commandes

        self.buttonConnect      = QPushButton()
        self.buttonConnect.setIcon(QIcon('icones/disconnected.png'))
        self.buttonConnect.setToolTip('connect to network')
        self.buttonConnect.setStyleSheet("background-color : red")
        self.buttonConnect.clicked.connect(self.startConnexion)
        commands.addWidget(self.buttonConnect)
        
        
        buttonConfig      = QPushButton()
        buttonConfig.setIcon(QIcon('icones/photo.png'))
        buttonConfig.setToolTip('get config of topics')
        buttonConfig.clicked.connect(self.commandConfig)
        commands.addWidget(buttonConfig)
        
        
        
        self.docked = QDockWidget("Commands", self)
        self.docked.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.docked.setFeatures(QDockWidget.DockWidgetFloatable |
                         QDockWidget.DockWidgetMovable)

        widget =  QWidget()
        widget.setLayout( commands)
         
        self.docked.setWidget(widget)#addLayout(self.displays_rec )#layout().addWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docked)
        
        #==================================
        # text box
        #==================================
        
        self.textbox = QTextEdit()
        self.textbox.setFont(TEXT_FONT)
        self.textbox.setMinimumSize(300, 100)
        self.text_update.connect(self.append_text)
        sys.stdout = self
        
        #self.vlayout.addWidget(self.textbox)
        self.tabs.addTab(self.textbox,'console')
        

        #==================================
        # default parameters
        #==================================
        
        self.server_ip   = 'localhost'
        self.server_port = 1883
        self.hostname    = 'C2-master' 
        
        #==================================
        #detections settings
        #==================================
        self.clients      = []
        self.topic        = None
        self.topicList    = ['config']
 
    def selectDevice(self,device):
        if  not device.isnumeric():
            return None
        for _client in self.clients:
            val =  _client.selectDevice(int(device))
            if val :
                return val
        return None
    def openMenu(self,position):
        
        indexes = self.tree.selectedItems()
        device = None
        if indexes:
            device = self.selectDevice(indexes[0].text(0))
        if device == None:
            return
 
        menu = QMenu()
        menu.setTitle("commands of "+device.type.name)
        for _command in device.commandList:
                Action = menu.addAction(_command)
                if _command =="start":
                    Action.triggered.connect(device.start)
                elif _command =="stop":
                    Action.triggered.connect(device.stop)
                elif _command =="picture":
                    Action.triggered.connect(device.picture)
                elif _command =="signal":
                    Action.triggered.connect(device.signal)
  
          
                
           
            
        menu.exec(self.tree.mapToGlobal(position))
        
        
    def commandConfig(self):
        if self.topic:
            self.topic.sendMessage('cmnd/config',0)
            print("message cmnd/config sended")
    def append_text(self, text):
        cur = self.textbox.textCursor()     # Move cursor to end of text
        cur.movePosition(QTextCursor.End) 
        s = str(text)
        while s:
            head,sep,s = s.partition("\n")  # Split line at LF
            cur.insertText(head)            # Insert text at cursor
            if sep:                         # New line if LF
                cur.insertBlock()
        self.textbox.setTextCursor(cur)     # Update visible cursor

    def on_connection(self):
        
        self.buttonConnect.setIcon(QIcon('icones/connected.png'))
        self.buttonConnect.setToolTip('connected to network')
        self.buttonConnect.setStyleSheet("background-color : green")
        
        self.topic.discover()
    def clientExists(self,hostname):

        for _client in self.clients:
            if _client.name == hostname:
                return True
        return False
    def receiveClient(self,jsonMsg):
        if not validateJSON(jsonMsg) or  jsonMsg==str(0):
            print("error in json file with new client");
            return
 
        file = json.loads(jsonMsg)

     
        if file.get("hostname") is not None and not self.clientExists(file['hostname']):
      
            _client = client()
            _client.setTopic(self.topic)
       
            _client.setName(file['hostname'])
            
            _client.setSensors(file['sensors'])
            
            _client.addTree(self.treeClients)
        
            for _device in _client.devices:

                self.tabs.addTab(_device,str(_device.id)+'_'+_device.name)
          
            self.clients.append(_client)
    def diffuseMessage(self,messages):
   
        for _client in self.clients:
            _client.receiveMessage(messages[0])
    def startConnexion(self):
        if self.topic==None:
           self.topic=topic(self.server_ip,self.server_port,self.hostname)
           self.topic.is_connected  =  self.on_connection
           self.topic.receiveClient.connect(self.receiveClient)
           self.topic.emitMessage.connect(self.diffuseMessage)
           for _topic in self.topicList:
                self.topic.subscribe(_topic)
           
        self.topic.start()
    def connexionSettings(self):
        dlg = connexionSettings()
        dlg.setIP(self.server_ip)
        dlg.setPort(self.server_port)
        dlg.setName(self.hostname)
        
        if dlg.exec():
            print("settings ok")
            self.server_ip   =  dlg.IPAddress.text()
            self.server_port =  int(dlg.port.text())
            self.hostname    =  dlg.hostname.text()
        else:
            print("settings cancelled")
    def ShowCommandsWidget(self):
       pass
    def ShowControls(self):
       pass
#         if self.showControlAction.isChecked()  :
#             self.textbox.show()
#         else:
#             self.textbox.hide()
    def resizeEvent(self,event):
        print("Window has been resize")
        h = self.height()*0.5
        w = self.width()*0.5
        QMainWindow.resizeEvent(self,event)
    
    
    # Window is closing: stop video capture
    def closeEvent(self, event):
        global capturing
        capturing = False
    def write(self, text):
        self.text_update.emit(str(text))
if __name__ == '__main__':
#     if len(sys.argv) > 1:
#         try:
#             camera_num = int(sys.argv[1])
#         except:
#             camera_num = 0
#     if camera_num < 1:
#         print("Invalid camera number '%s'" % sys.argv[1])
#     else:
#         
#         qp = QPalette()
#         qp.setColor(QPalette.ButtonText, Qt.black)
#         qp.setColor(QPalette.Window, Qt.black)
#         qp.setColor(QPalette.Button, Qt.gray)
        
        
        app = QApplication(sys.argv)
 #       app.setPalette(qp)
        qtmodern.styles.dark(app)
        win =  qtmodern.windows.ModernWindow(MyWindow())
        #win = MyWindow()
        win.show()
        win.setWindowTitle(VERSION)
        
        sys.exit(app.exec_())
