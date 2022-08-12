import os.path
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
from PyQt5.QtCore import QCoreApplication, QDir, QFileInfo, QUrl, Qt, QEvent, QTimer
from PyQt5 import uic


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 加载ui文件
        self.ui = uic.loadUi("./res/ui/MainWindow.ui")
        self.player = QMediaPlayer()


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.show()
    app.exec()
