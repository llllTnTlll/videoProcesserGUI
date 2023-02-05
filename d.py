import sys
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGroupBox, QRubberBand


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QRubberBand Example')
        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(10, 10, 400, 400)
        self.label = QLabel(self.groupBox)
        self.label.setGeometry(10, 10, 380, 380)
        self.label.setPixmap(QPixmap(r'C:\Users\lzy99\OneDrive\图片\屏幕快照\2022-07-18.png'))
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.label)
        self.origin = None

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
