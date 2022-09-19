from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
from PyQt5.QtCore import *
from PyQt5 import uic
import sys
import cv2 as cv
from pathlib import Path
import time
import resultWindow
import numpy as np


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
        self.is_slider_pressed = False

    def run(self):
        while True:
            if self.player_status != VideoStatus.VIDEO_PLAY:
                continue
            if not self.is_slider_pressed:
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

    def slider_pressed(self):
        self.is_slider_pressed = True

    def slider_released(self):
        self.is_slider_pressed = False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 属性
        self.VIDEO_PATH = None
        self.VIDEO_FPS = 0
        self.VIDEO_FRAME_COUNT = 0
        self.VIDEO_FRAME_NOW = 0
        self.ROI_COORD_LT = (130, 160)
        self.ROI_COORD_RB = (250, 290)
        self.ROI_COLOR = (255, 0, 0)
        self.ROI_THICKNESS = 2
        self.SCALE_RATE = 0.3
        self.CURTAIN_SIZE = (600, 400)

        self.video_capture = cv.VideoCapture()

        self.resultWindow = resultWindow.ResultWindow()

        # 加载ui
        self.ui = uic.loadUi("./res/ui/MainWindow.ui")
        self.reset_coord()

        # 按键功能
        self.ui.playBtn.clicked.connect(self.play_or_pause)
        self.ui.analysisBtn.clicked.connect(self.analysis)

        # 动作
        self.ui.openAct.triggered.connect(self.open_act)

        # 视频播放
        self.player = VideoPlayer()
        self.player.signals.refresh_signal.connect(self.frame_refresh)
        self.player.start()
        self.ui.videoSlider.sliderMoved.connect(self.slider_moved)
        self.ui.videoSlider.sliderReleased.connect(self.slider_released)
        self.ui.VideoLabel.setScaledContents(True)

        self.ui.LineEdit_x1.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_x2.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_y1.editingFinished.connect(self.coord_changed)
        self.ui.LineEdit_y2.editingFinished.connect(self.coord_changed)

        self.behaviors_lock(True)
        self.set_curtain()

    # 基本功能与按键响应
    def behaviors_lock(self, status):
        if status:
            self.ui.behaviors_groupBox.setEnabled(False)
        elif not status:
            self.ui.behaviors_groupBox.setEnabled(True)

    def open_act(self):
        cap = "open video file"
        filt = "视频文件(*.wmv *.avi *.mp4 *.mov)"
        path = QFileDialog.getOpenFileName(caption=cap, filter=filt)[0]
        if path != "" and Path(path).is_file():
            self.video_init(path)
            self.video_play(is_first=True)
            self.behaviors_lock(False)

    def analysis(self):
        self.resultWindow.ROI_COORD_LT = self.ROI_COORD_LT
        self.resultWindow.ROI_COORD_RB = self.ROI_COORD_RB
        self.resultWindow.VIDEO_PATH = self.VIDEO_PATH
        self.resultWindow.analysis()
        self.resultWindow.ui.show()

    # 视频相关
    def play_or_pause(self):
        """视频暂停播放按钮"""
        print(self.player.player_status)
        if self.player.player_status == VideoStatus.VIDEO_PLAY:
            self.video_pause()
        elif self.player.player_status == VideoStatus.VIDEO_PAUSE:
            self.video_play()

    def display_progress(self):
        position = int((self.VIDEO_FRAME_NOW/self.VIDEO_FRAME_COUNT) * 100)
        if not self.player.is_slider_pressed:
            self.ui.videoSlider.setSliderPosition(position)
        self.ui.ratioLabel.setText("Frame {} of {}".format(str(self.VIDEO_FRAME_NOW), str(self.VIDEO_FRAME_COUNT)))

    def set_progress(self, frame_now, frame_count=None):
        if frame_count is not None:
            self.VIDEO_FRAME_COUNT = frame_count
        self.VIDEO_FRAME_NOW = frame_now
        self.display_progress()

    def video_init(self, path):
        # 存储路径
        self.VIDEO_PATH = path

        # 获取视频默认帧速率与总帧数
        self.video_capture.open(self.VIDEO_PATH)
        self.player.set_fps(int(self.video_capture.get(cv.CAP_PROP_FPS)))

        # 设置进度label
        self.set_progress(0, int(self.video_capture.get(cv.CAP_PROP_FRAME_COUNT)))

    def video_play(self, is_first=False):
        if self.player.player_status != VideoStatus.VIDEO_NOT_LOADED or is_first:
            self.player.play()
            self.ui.playBtn.setStyleSheet("QPushButton{qproperty-icon:url(res/icon/pause.png)}")

    def video_pause(self):
        if self.player.player_status != VideoStatus.VIDEO_NOT_LOADED:
            self.player.pause()
            self.ui.playBtn.setStyleSheet("QPushButton{qproperty-icon:url(res/icon/play.png)}")

    def video_reset(self):
        self.VIDEO_FRAME_NOW = 0
        self.video_capture.set(cv.CAP_PROP_POS_FRAMES, 0)
        self.video_pause()

    def slider_moved(self, position):
        self.player.slider_pressed()
        if self.player.player_status != VideoStatus.VIDEO_NOT_LOADED:
            target_frame = int((position / 100) * self.VIDEO_FRAME_COUNT)
            self.video_capture.set(cv.CAP_PROP_POS_FRAMES, target_frame)
            self.set_progress(target_frame)

    def slider_released(self):
        self.player.slider_released()

    def set_curtain(self):
        """初始化幕布"""
        img = np.zeros((self.CURTAIN_SIZE[0], self.CURTAIN_SIZE[1], 3), np.uint8)
        self.set_pixmap(img, self.CURTAIN_SIZE[0], self.CURTAIN_SIZE[1])

    def set_pixmap(self, img, width, height):
        """帧格式转化与label刷新"""
        temp_image = QImage(img.flatten(), width, height, QImage.Format_RGB888)
        temp_pixmap = QPixmap.fromImage(temp_image)
        self.ui.VideoLabel.setPixmap(temp_pixmap)

    def draw_roi(self, rgb):
        rgb = cv.rectangle(rgb, self.ROI_COORD_LT, self.ROI_COORD_RB, self.ROI_COLOR, self.ROI_THICKNESS)
        return rgb

    def frame_refresh(self):
        """帧重绘"""
        if self.video_capture.isOpened():
            flag, frame = self.video_capture.read()
            if flag:
                frame = cv.resize(frame, (0, 0), fx=self.SCALE_RATE, fy=self.SCALE_RATE)
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    self.set_pixmap(self.draw_roi(rgb), width, height)
                elif frame.ndim == 2:
                    rgb = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
                    self.set_pixmap(self.draw_roi(rgb), width, height)
                self.VIDEO_FRAME_NOW += 1
                self.display_progress()

            else:
                print("read failed, no frame data")
                self.video_reset()
        else:
            print("open file or capturing device error, init again")

    # 兴趣区域相关
    def reset_coord(self):
        self.ui.LineEdit_x1.setText("{}".format(self.ROI_COORD_LT[0]))
        self.ui.LineEdit_y1.setText("{}".format(self.ROI_COORD_LT[1]))
        self.ui.LineEdit_x2.setText("{}".format(self.ROI_COORD_RB[0]))
        self.ui.LineEdit_y2.setText("{}".format(self.ROI_COORD_RB[1]))

    def coord_changed(self):
        try:
            p1 = (int(self.ui.LineEdit_x1.text()), int(self.ui.LineEdit_y1.text()))
            p2 = (int(self.ui.LineEdit_x2.text()), int(self.ui.LineEdit_y2.text()))
        except ValueError:
            self.reset_coord()
            QMessageBox(QMessageBox.Warning, 'Warning', '请输入整数型坐标值').exec()
            return

        if p1[0] < p2[0] and p1[1] < p2[1]:
            self.ROI_COORD_LT = p1
            self.ROI_COORD_RB = p2
        else:
            self.reset_coord()
            QMessageBox(QMessageBox.Warning, 'Warning', '坐标输入非法').exec()
            return


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.show()
    app.exec()
