from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QRubberBand, QGroupBox, QLabel
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QImage, QPixmap, QPainter


class RoiWindow(QWidget):
    def __init__(self):
        super().__init__()
        super().__init__()
        self.setWindowTitle('QRubberBand Example')
        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(10, 10, 400, 400)
        self.label = QLabel(self.groupBox)
        self.label.setGeometry(10, 10, 380, 380)
        self.label.setScaledContents(True)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.label)
        self.origin = None

    def set_roilabel(self, pixmap):
        self.label.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin:
            return
        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            left_top = self.label.mapFrom(self, self.rubberBand.geometry().topLeft())
            right_bottom = self.label.mapFrom(self, self.rubberBand.geometry().bottomRight())
            print(left_top, right_bottom)
            self.origin = None
            self.rubberBand.hide()
            self.rubberBand.hide()
