import cv2
import numpy as np
import paho.mqtt.client as mqtt
import os
import time
from devices import  device,SENSOR
from io import BytesIO
import glob
#from itertools import count

#iid = count()

try:
    import Queue as Queue
except:
    import queue as Queue
  
 
try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import  QTimer, QPoint, pyqtSignal, QThread,QDateTime , pyqtSignal, pyqtSlot
    from PyQt5.QtWidgets import QMenu,QApplication, QMainWindow, QTextEdit, QLabel, QComboBox, QSlider, QCheckBox,QDialog,QLineEdit, QDialogButtonBox,QPushButton
    from PyQt5.QtWidgets import QTreeWidgetItem,QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt5.QtGui import QFont, QIcon,QPainter, QPixmap,QImage, QTextCursor,QStandardItemModel, QPalette
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QPoint, pyqtSignal, pyqtSlot
    from PyQt4.QtGui import QMenu,QApplication, QMainWindow, QTextEdit, QLabel, QComboBox,QSlider
    from PyQt4.QtGui import QTreeWidgetItem,QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt4.QtGui import QFont, QIcon,QPainter,QPixmap, QImage, QTextCursor

DISP_MSEC   = 50                # Delay between display cycles
        
 
class esp32Cam(QWidget,device):
    
    def __init__(self):
        QWidget.__init__(self)
        device.__init__(self)
   
        
        self.type = SENSOR.CAMERA
        self.tree = None
        self.parameters = []
        self.topicList   =['picture','video','signalStrength']
        self.commandList = []
        self.tree         = None
 
        #self.widget       = QWidget()
        self.label   = QLabel()
  
        layout = QVBoxLayout()
        layout.addWidget(self.label )
 
        self.setLayout(layout)
        
        
        buttons = QHBoxLayout()
        self.rec   = QPushButton('start')
        #rec.setIcon(QIcon('icones/photo.png'))
        self.rec.clicked.connect(self.recording)
        snap  = QPushButton('capture')
        #snap.setIcon(QIcon('icones/photo.png'))
        snap.clicked.connect(self.capture)
        buttons.addWidget(self.rec)
        buttons.addWidget(snap)
        layout.addLayout(buttons)
        #===============================
        #video
        #===============================
        self.timer        = QTimer(self)
        self.videoCapture = False
        self._path        ='' 
        self.image_queue  = Queue.Queue()
        self.timer.timeout.connect(lambda:self.displayPicture(self.image_queue))              
    
    def capture(self):
        _path = './save_images/device_'+str(self.id)
        if not os.path.exists( _path):
            os.mkdir( _path)
        pix = self.label.grab()
        pix.save(_path+'/'+QDateTime.currentDateTime().toString('yyyy-MM-ddTHH:mm:ss.z')+'.png') 
    def recording(self):
         self._path = './save_videos/device_'+str(self.id)
         if not os.path.exists(self._path ):
                os.mkdir(self._path )
         if self.videoCapture == False:
             self.videoCapture = True
             self.rec.setText('stop')
         else:
             self.videoCapture = False
             self.rec.setText('start')
             _locpath = self._path+'/'+QDateTime.currentDateTime().toString('yyyy-MM-ddTHH:mm:ss.z')+'.avi'
             out = cv2.VideoWriter(_locpath,cv2.VideoWriter_fourcc(*'XVID'), 4.0, (640,480))
             files = glob.glob(self._path +'/*.png')
             files.sort(key = os.path.getmtime)
             for filename in files:
                img = cv2.imread(filename)
                out.write(img)

             out.release()
             for filename in glob.glob(self._path +'/*.png'):
                os.remove(filename)
            
    def start(self):
        cmnd = 'cmnd/'+self.name+'/start'
        self.command(cmnd)
    def signal(self):
        cmnd = 'cmnd/'+self.name+'/signalStrength'
        self.command(cmnd)
    def stop(self):
        cmnd = 'cmnd/'+self.name+'/stop'
        self.command(cmnd)
    
    def picture(self):
        cmnd = 'cmnd/'+self.name+'/picture'
        self.command(cmnd)
    def command(self,cmnd):
        pass
    
    def displayPicture(self, imageq):
        
        if not imageq.empty():
            image = imageq.get()
            w = self.label.width()
            h = self.label.height()
            p = image.scaled(w,h,Qt.KeepAspectRatio)
            self.label.setPixmap(QPixmap.fromImage(p))
            if self.videoCapture:
                 _locpath = self._path+'/'+QDateTime.currentDateTime().toString('yyyy-MM-ddTHH:mm:ss.z')+'.png'
                 image.save(_locpath)
  
    def queuePicture(self,_bytes):
        
        #with open("imageToSave.png","wb") as fh:
         #   fh.write(_bytes)

        #data  = bytearray(_bytes)
        #data  = BytesIO(data)
        arr = np.fromstring(_bytes,np.uint8)
        img = cv2.imdecode(arr,1)
        image_gray = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        #cv2.imwrite('image.png',image_gray)
        
        h,w,ch=image_gray.shape
       
        image = QImage(image_gray.data,w,h,ch*w,QImage.Format_RGB888)
        if  self.image_queue.qsize() < 2:
            self.image_queue.put(image)
        #p = image.scaled(self.width(),self.height(),Qt.KeepAspectRatio)
        #self.label.setPixmap(QPixmap.fromImage(p))
       
    def setName(self,name):
        self.name = name
    def setType(self,_type):
        
        for _sensorType in SENSOR.list():
            if _sensorType.value == _type:
                self.type =_sensorType
                return
    def setCommands(self,_commands):
        
        for _com in _commands.split(','):
            self.commandList.append(_com)
 
    def addTree(self,_tree):
        self.tree  = QTreeWidgetItem(_tree)
        self.tree.setText(0,str(self.id));  
        self.tree.setText(1,self.type.name);     
    def receiveMessage(self,_msg):

        message = _msg.topic.split('/')
        if len(message)!=3:
            return
 
        if message[0] == 'sensor' and message[1] == self.name:
            if message[2]=='picture' or message[2]=='video' :
                if not self.timer.isActive():
                    self.timer.start(DISP_MSEC)
                self.queuePicture(_msg.payload)
            if message[2]=='signalStrength':
                print(_msg.payload.decode("utf-8"))
           
                value = float(_msg.payload.decode("utf-8"))
                if value >= 80:
                    self.tree.setIcon(0,QIcon('./icones/wifi_good.png'));
                elif value < 80 and value >= 60 :
                    self.tree.setIcon(0,QIcon('./icones/wifi_medium.png'));
                elif value < 60 :
                    self.tree.setIcon(0,QIcon('./icones/wifi_bad.png'));