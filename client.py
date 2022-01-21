try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import QTimer, QPoint, QRect, pyqtSignal, QThread,QDateTime, pyqtSlot
    from PyQt5.QtWidgets import QSizePolicy, QApplication, QMainWindow, QTextEdit, QLabel, QComboBox, QSlider, QMessageBox, QCheckBox,QDialog,QLineEdit, QDialogButtonBox,QPushButton
    from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget,QWidget, QAction, QVBoxLayout, QHBoxLayout, QDockWidget,QFrame
    from PyQt5.QtGui import QFont, QPainter, QImage, QPixmap,QTextCursor,QStandardItemModel,QStandardItem, QPalette, QIcon
else:
    from PyQt4.QtCore import Qt, QPoint, QRect, pyqtSignal, QTimer, QPoint,pyqtSlot
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel, QComboBox,QSlider, QMessageBox
    from PyQt4.QtGui import QTreeWidgetItem, QTreeWidget,QWidget, QAction, QVBoxLayout, QHBoxLayout,QDockWidget
    from PyQt4.QtGui import QFont, QPainter, QImage, QPixmap, QTextCursor,QStandardItemModel, QStandardItem,QPalette, QIcon


from espCam import esp32Cam

class client():
    def __init__(self):
        self.name    = "none"
        self.devices = []  
        self.tree    = None
        self.topic   = None
   
    def setName(self,name):
        self.name =   name

    def setTopic(self,_topic):
        self.topic   = _topic

    
        
    def receiveMessage(self, message):
    
        
        if message.topic =="config":
            self.receiveClient(str(message.payload.decode("utf-8")))
            return
            
        for _device in  self.devices:
            _device.receiveMessage(message)
       
            
    def on_command(self,cmnd):
        print(cmnd)
        if self.topic :
            self.topic.sendMessage(cmnd,0)
    def subscribes(self,_type,topclist):
        
        for _topic in topclist:
             if self.topic :
                print('in subscribe')
                print(_type +'/'+ self.name+'/'+_topic)
                self.topic.subscribe(_type +'/'+ self.name+'/'+_topic)
        
    def setSensors(self,_sensors):
 
        for _sensor in _sensors:
  
            if _sensor['type'] == "ESP32CAM":
                
                print('---> reçu')
                self.devices.append(esp32Cam())
                print('---> reçu')
                self.devices[-1].setName(self.name)
                print('---> reçu')
                self.devices[-1].setCommands(_sensor['commands'])
                print('---> reçu')
                self.devices[-1].command  = self.on_command
                self.subscribes('sensor',self.devices[-1].topicList)
                print('---> reçu')
    def selectDevice(self,_id):
        for _device in self.devices :
            if _device.id == _id:
                return _device
        return None
        
          
    def addTree(self,_tree):
        self.tree  = QTreeWidgetItem(_tree)
        self.tree.setText(0,self.name);
        
        for _device in self.devices :
       
            _device.addTree(self.tree)
   
         
            
        
        
    