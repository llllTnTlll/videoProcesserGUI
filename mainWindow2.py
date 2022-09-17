from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
from PyQt5.QtCore import *
from PyQt5 import uic
import sys
import cv2 as cv
from pathlib import Path
import time


class VideoStatus:
    # -1为未加载 1为播放 0为暂停
    VIDEO_NOT_LOADED = -1
    VIDEO_PAUSE = 0
    VIDEO_PLAY = 1


class Signals(QObject):
    refresh_signal = pyqtSignal()


class VideoPlayer(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.player_status = VideoStatus.VIDEO_NOT_LOADED
        self.refresh_rate = 20.0
        self.mutex = QMutex()
        self.signals = Signals()

    def run(self):
        while True:
            if self.player_status != VideoStatus.VIDEO_PLAY:
                continue
            self.signals.refresh_signal.emit()
            time.sleep(1 / self.refresh_rate)

    def play(self):
        with QMutexLocker(self.mutex):
            self.player_status = VideoStatus.VIDEO_PLAY

    def pause(self):
        with QMutexLocker(self.mutex):
            self.player_status = VideoStatus.VIDEO_PAUSE

    def set_fps(self, fps):
        self.refresh_rate = fps


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 属性
        self.VIDEO_PATH = None
        self.VIDEO_FPS = 0
        self.ROI_COORD_LT = (100, 100)
        self.ROI_COORD_RB = (200, 200)

        self.video_capture = cv.VideoCapture()

        # 加载ui
        self.ui = uic.loadUi("./res/ui/MainWindow.ui")
        self.reset_coord()

        # 按键功能
        self.ui.playBtn.clicked.connect(self.play_or_pause)

        # 动作
        self.ui.openAct.triggered.connect(self.open_act)

        # timer
        self.player = VideoPlayer()
        self.player.signals.refresh_signal.connect(self.frame_refresh)
        self.player.start()

        self.ui.VideoLabel.setScaledContents(True)

        self.ui.LineEdit_x1.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_x2.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_y1.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_y2.editingFinished.connect(self.coord_changed)

    def play_or_pause(self):
        pass

    def reset_coord(self):
        self.ui.LineEdit_x1.setText("{}".format(self.ROI_COORD_LT[0]))
        self.ui.LineEdit_y1.setText("{}".format(self.ROI_COORD_LT[1]))
        self.ui.LineEdit_x2.setText("{}".format(self.ROI_COORD_RB[0]))
        self.ui.LineEdit_y2.setText("{}".format(self.ROI_COORD_RB[1]))

    def set_pixmap(self, img, width, height):
        temp_image = QImage(img.flatten(), width, height, QImage.Format_RGB888)
        temp_pixmap = QPixmap.fromImage(temp_image)
        self.ui.VideoLabel.setPixmap(temp_pixmap)

    def draw_roi(self, rgb):
        rgb = cv.rectangle(rgb, self.ROI_COORD_LT, self.ROI_COORD_RB, (255, 0, 0), 2)
        return rgb

    def open_act(self):
        cap = "open video file"
        filt = "视频文件(*.wmv *.avi *.mp4 *.mov)"
        path = QFileDialog.getOpenFileName(caption=cap, filter=filt)[0]
        if path != "" and Path(path).is_file():
            # 存储路径
            self.VIDEO_PATH = path

            # 获取视频默认帧速率
            self.video_capture.open("./samples/10Hz.mp4")
            self.player.set_fps(self.video_capture.get(cv.CAP_PROP_FPS))

            # 自动播放视频
            self.player.player_status = VideoStatus.VIDEO_PLAY
        else:
            pass

    def frame_refresh(self):
        if self.video_capture.isOpened():
            flag, frame = self.video_capture.read()
            if flag:
                frame = cv.resize(frame, (0, 0), fx=0.3, fy=0.3)
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    self.set_pixmap(self.draw_roi(rgb), width, height)
                elif frame.ndim == 2:
                    rgb = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
                    self.set_pixmap(self.draw_roi(rgb), width, height)

            else:
                print("read failed, no frame data")
                self.player.pause()
        else:
            print("open file or capturing device error, init again")

    def coord_changed(self):
        try:
            p1 = (int(self.ui.LineEdit_x1.text()), int(self.ui.LineEdit_y1.text()))
            p2 = (int(self.ui.LineEdit_x2.text()), int(self.ui.LineEdit_y2.text()))
        except ValueError:
            self.reset_coord()
            QMessageBox(QMessageBox.Warning, 'Warning', '坐标输入非法').exec()


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.show()
    app.exec()
