from PyQt5 import uic
from PyQt5.QtCore import Qt, QRect, QSize, QEvent
from PyQt5.QtWidgets import QRubberBand, QWidget
from ops import Signals


class RoiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./res/ui/roiWindow.ui")
        self.ui.RoiLabel.setScaledContents(True)
        self.ui.RoiLabel.setMouseTracking(True)
        self.ui.RoiLabel.installEventFilter(self)
        self.signals = Signals()

        self.origin = None
        self.selected = None
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.ui.RoiLabel)

    def set_roilabel(self, pixmap):
        self.ui.RoiLabel.setPixmap(pixmap)

    def eventFilter(self, source, event):
        if source == self.ui.RoiLabel and event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        if source == self.ui.RoiLabel and event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        if source == self.ui.RoiLabel and event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
            return True
        return super().eventFilter(source, event)


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
            self.rubberBand.hide()
            selected_rect = self.rubberBand.geometry()
            x1, y1, x2, y2 = selected_rect.getCoords()
            self.format_coord(x1, y1, x2, y2)
            # self.set_textlabel()
            self.signals.roi_selected_signal.emit(self.selected)
            self.ui.close()

    def format_coord(self, x1, y1, x2, y2):
        pixmap = self.ui.RoiLabel.pixmap()
        width = pixmap.width()
        height = pixmap.height()
        x1 = min(max(0, x1), width - 1)
        y1 = min(max(0, y1), height - 1)
        x2 = min(max(0, x2), width - 1)
        y2 = min(max(0, y2), height - 1)
        self.selected = [x1, y1, x2, y2]

    def set_textlabel(self):
        self.ui.label_x1.setText("X1: {}".format(self.selected[0]))
        self.ui.label_y1.setText("Y1: {}".format(self.selected[1]))
        self.ui.label_x2.setText("X2: {}".format(self.selected[2]))
        self.ui.label_y2.setText("Y2: {}".format(self.selected[3]))






