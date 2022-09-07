from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
from PyQt5.QtCore import QCoreApplication, QObject, QFileInfo, QUrl, Qt, QEvent, QThread, QMutexLocker, QMutex, pyqtBoundSignal
from PyQt5 import uic
import sys
import cv2 as cv
from pathlib import Path
import time


class VideoOps:
    # -1为未加载 1为播放 0为暂停
    VIDEO_NOT_LOADED = -1
    VIDEO_PAUSE = 0
    VIDEO_PLAY = 1


class VideoTimer(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.stopped = False
        self.refresh_rate = 20
        self.refresh_signal = pyqtBoundSignal()
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.refresh_signal.emit()
            time.sleep(1 / self.refresh_rate)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.refresh_rate = fps


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 属性
        self.VIDEO_PATH = None
        self.VIDEO_FPS = 0
        self.PLAY_STATUS = VideoOps.VIDEO_NOT_LOADED

        self.video_capture = cv.VideoCapture()

        # 加载ui文件
        self.ui = uic.loadUi("./res/ui/MainWindow.ui")

        # 按键功能
        self.ui.playBtn.clicked.connect(self.play_or_pause)

        # 动作
        self.ui.openAct.triggered.connect(self.open_act)

        # timer
        self.timer = VideoTimer()
        self.timer.refresh_signal.signal[str].connect(self.frame_refresh)

    def play_or_pause(self):
        if self.PLAY_STATUS != VideoOps.VIDEO_NOT_LOADED:
            if self.PLAY_STATUS == VideoOps.VIDEO_PLAY:
                self.PLAY_STATUS = VideoOps.VIDEO_PAUSE
            if self.PLAY_STATUS == VideoOps.VIDEO_PAUSE:
                self.PLAY_STATUS = VideoOps.VIDEO_PLAY
        return

    def open_act(self):
        cap = "open video file"
        filt = "视频文件(*.wmv *.avi *.mp4 *.mov)"
        path = QFileDialog.getOpenFileName(caption=cap, filter=filt)[0]
        if path != "" and Path(path).is_file():
            # 存储路径
            self.VIDEO_PATH = path

            # 获取视频默认帧速率
            self.video_capture.open("./samples/10Hz.mp4")
            self.VIDEO_FPS = self.video_capture.get(cv.CAP_PROP_FPS)

            # 自动播放视频
            self.PLAY_STATUS = VideoOps.VIDEO_PLAY
        else:
            pass

    def frame_refresh(self):
        pass


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.show()
    app.exec()
