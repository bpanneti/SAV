from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from readGeoTiff import cartographie as cartoFile
import matplotlib
matplotlib.use('Qt5Agg')
import sys


from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

from matplotlib.patches import Circle, Wedge, Polygon

class GIS(QWidget):

    def __init__(self):
        super(GIS, self).__init__()
        self.view()
        self.carte = cartoFile()
        #self.carte.read(self.fileName,TYPE_CARTO.CARTO)
        self.carte.display(self.axes)
    def setBackgroundColor(self,color):
         self.fig.set_facecolor(color)
         self.axes.xaxis.label.set_color('yellow')        #setting up X-axis label color to yellow
         self.axes.yaxis.label.set_color('yellow')          #setting up Y-axis label color to blue
         self.axes.tick_params(axis='x', colors='yellow')    #setting up X-axis tick color to red
         self.axes.tick_params(axis='y', colors='yellow')  #setting up Y-axis tick color to black

         #ax.spines['left'].set_color('red')        # setting up Y-axis tick color to red
         #ax.spines['top'].set_color('red')       
    def view(self):
            self.fig        =  Figure((5.0, 4.0), dpi=100)
            self.axes       = self.fig.add_subplot(111)
            self.axes.grid(True)
            self.canvas     = FigureCanvas(self.fig)
            self.canvas.setFocusPolicy(Qt.StrongFocus)
            self.canvas.setFocus()
            self.canvas.draw()
            self.canvas.show()
            
            self.toolBar = NavigationToolbar(self.canvas, self)
          
        
                        
def main():
     

    app = QApplication(sys.argv)
    window = GIS()
    window.show()
    app.exec()
   
        
if __name__ == "__main__":
    main() 