from enum import Enum
from itertools import count

try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import QTimer, QPoint, QRect, pyqtSignal, QThread,QDateTime
    from PyQt5.QtWidgets import QSizePolicy, QApplication, QMainWindow, QTextEdit, QLabel, QComboBox, QSlider, QCheckBox,QDialog,QLineEdit, QDialogButtonBox,QPushButton
    from PyQt5.QtWidgets import QTreeWidgetItem,QWidget, QAction, QVBoxLayout, QHBoxLayout, QDockWidget,QFrame
    from PyQt5.QtGui import QFont, QPainter, QImage, QPixmap,QTextCursor,QStandardItemModel,QStandardItem, QPalette, QIcon
else:
    from PyQt4.QtCore import Qt, QPoint, QRect, pyqtSignal, QTimer, QPoint
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel, QComboBox,QSlider
    from PyQt4.QtGui import QTreeWidgetItem,QWidget, QAction, QVBoxLayout, QHBoxLayout,QDockWidget
    from PyQt4.QtGui import QFont, QPainter, QImage, QPixmap, QTextCursor,QStandardItemModel, QStandardItem,QPalette, QIcon
 
class SENSOR(Enum):
    UNKNOWN = 0
    CAMERA  = 1
    C2      = 2
    @staticmethod
    def list():
        return list(map(lambda c :c,SENSOR))

iid = count()

class device(object):

    
    def __init__(self):

        self.commandList = []
        self.tree      = None
        self.type = SENSOR.UNKNOWN
        self.id   = next(iid)
        self.name = 'none'
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
        