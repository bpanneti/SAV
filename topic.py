import numpy as np
import paho.mqtt.client as mqtt
import os
import time


try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import QTimer, QPoint, pyqtSignal, QThread,QDateTime 
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QMessageBox, QComboBox, QSlider, QCheckBox,QDialog,QLineEdit, QDialogButtonBox,QPushButton
    from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor,QStandardItemModel, QPalette
    from PyQt5.QtNetwork import QHostAddress
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QPoint, QHostAddress
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel, QComboBox,QSlider,  QMessageBox
    from PyQt4.QtGui import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt4.QtGui import QFont, QPainter, QImage, QTextCursor
    from PyQt4.QtNetwork import QHostAddress
try:
    import Queue as Queue
except:
    import queue as Queue
  
 


 
MainTopic = "python"
client_id = f'python-mqtt-{np.random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

 

class settingsDlg(QDialog):
    
    def __init__(self):
        QDialog.__init__(self)
        
        self.setWindowTitle("Connexion settings")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonbox = QDialogButtonBox(QBtn)
        self.buttonbox.accepted.connect(self.acceptdata)
        self.buttonbox.rejected.connect(self.rejectdata)
        
        Layout = QVBoxLayout()
        
        #IP address
        LayoutIP       = QHBoxLayout()
        label          = QLabel("IP server")
        self.IPAddress = QLineEdit()
        LayoutIP.addWidget(label)
        LayoutIP.addWidget(self.IPAddress )
        
        LayoutPort     = QHBoxLayout()
        labelp         = QLabel("port")
        self.port      = QLineEdit()
        LayoutPort.addWidget(labelp)
        LayoutPort.addWidget(self.port ) 
        LayoutHostname = QHBoxLayout()
        labelh         = QLabel("hostname")
        self.hostname  = QLineEdit()
        LayoutHostname.addWidget(labelh)
        LayoutHostname.addWidget(self.hostname)

        
        Layout.addLayout(LayoutHostname)
        Layout.addLayout(LayoutIP)
        Layout.addLayout(LayoutPort)
        
        Layout.addWidget(self.buttonbox)
        self.setLayout(Layout)
        
        
        self.IPAddress.setText('0.0.0.0')
        self.port.setText('8888')
        self.hostname.setText('none')
    def setIP(self,server_ip):
   
        self.IPAddress.setText(server_ip)
    def setPort(self,server_port):
        self.port.setText(str(server_port))
    def setName(self,hostname): 
        self.hostname.setText(hostname)
        
    def acceptdata(self):
        
        IP = QHostAddress(self.IPAddress.text())
        
        if IP.isNull():
            QMessageBox.critical(self,'Error','Invalid IP adress');
            return
        
        PORT = self.port.text()
        
        if not PORT.isnumeric():
            QMessageBox.critical(self,'Error','Invalid port number');
            return
       
        self.accept()
    def rejectdata(self):
        self.close()
        
class topic(QWidget):
    emitMessage     = pyqtSignal(list)
    receiveClient   = pyqtSignal('QString')
    def __init__(self,broker, port,nom):
        super().__init__()
        self.client = mqtt.Client(nom)
        self.connected = False
        self.client.connect(broker, port)
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
    def on_disconnect(self):
        self.connected = False
        self.client.loop_stop()
        
        print('server disconnected')
    def start(self):
        #start client connection
        self.client.loop_start()
    def stop(self):
        #stop client connection
        self.client.loop_stop()
        self.connected = False
    def sendMessage(self,topic,value):
        self.client.publish(topic,value)
 
    def on_message(self,mqttc, obj, message):
 
        if message.topic =="config":
            self.receiveClient.emit(str(message.payload.decode("utf-8")))
        else:

            self.emitMessage.emit([message])
        return
        '''
        print(message)
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
        '''
    def subscribe(self,top):
        self.client.subscribe(top)
    def is_connected(self):
        pass
 
        
    def discover(self):
        self.client.publish('config',0)
    def on_connect(self,client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            print (userdata)
            self.connected = True
            self.is_connected()
        else:
            print("Failed to connect, return code %d\n", rc)
            
          
if __name__ == '__main__':
   
    
    client = topic()
    client.start()
    while True:
         print('try publish')
         if client.connected:
             print('publish')
             client.client.publish(MainTopic, "Hello from a publish call")
             print('published')
         time.sleep(3)
         
    #subscribe(client)
