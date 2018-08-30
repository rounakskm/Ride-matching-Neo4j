
import sys, random
from PyQt4 import QtGui, QtCore

import time

class Example(QtGui.QDialog):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        self.setGeometry(0, 0, 1280, 690)
        self.setWindowTitle('Points')
        self.zoom = 0
        self.show()
        self.junctions = {}

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        self.drawLines(qp)
        self.drawCar(qp, 10, 10)
        qp.end()


        time.sleep(1)
        # qp = QtGui.QPainter()
        # qp.begin(self)
        # self.drawPoints(qp)
        # self.drawLines(qp)
        # self.drawCar(qp, 30, 30)
        # qp.end()


        # time.sleep(100)
        # qp = QtGui.QPainter()
        # qp.begin(self)
        # self.drawPoints(qp)
        # self.drawLines(qp)
        # self.drawCar(qp, 50, 30)
        # qp.end()

        # time.sleep(100)
        # qp = QtGui.QPainter()
        # qp.begin(self)
        # self.drawPoints(qp)
        # self.drawLines(qp)
        # self.drawCar(qp, 70, 70)
        # qp.end()
        
    def drawPoints(self, qp):
      
        qp.setPen(QtCore.Qt.red)
        size = self.size()
        
        file = open("oldenberg_nodes.txt").read()

        for line in file.split("\n"):
            if line:
                x = float(line.split(" ")[1])/10
                y = float(line.split(" ")[2])/15
                self.junctions[line.split(" ")[0]] = (x, y)
                qp.drawPoint(x, y)

        print(size.width())
        print(size.height())


    def drawCar(self, qp, xpos, ypos):

        qp.setPen(QtCore.Qt.blue)
        size = self.size()

        for i in range(1, 4):
            qp.drawPoint(xpos, ypos+i)
            qp.drawPoint(xpos, ypos-i)
            qp.drawPoint(xpos+i, ypos)
            qp.drawPoint(xpos-i, ypos)
            qp.drawPoint(xpos-i, ypos-i)
            qp.drawPoint(xpos+i, ypos-i)
            qp.drawPoint(xpos-i, ypos+i)
            qp.drawPoint(xpos+i, ypos+i)


    def drawLines(self, qp):
      
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)

        qp.setPen(pen)

        file = open("oldenberg_roads.txt").read()

        for line in file.split("\n"):
            if line:
                x1, y1 = self.junctions[line.split(" ")[1]]
                x2, y2 = self.junctions[line.split(" ")[2]]
                qp.drawLine(x1, y1, x2, y2)  
                
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
