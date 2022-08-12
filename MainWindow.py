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

        # 连接信号与槽
        self.ui.playBtn.clicked.connect(self.play_video)
        self.ui.pauseBtn.clicked.connect(self.pause_video)
        self.ui.fullscreenBtn.clicked.connect(self.full_screen)

        self.ui.openAct.triggered.connect(self.open_act)

        # 注册事件过滤器
        self.ui.videoWidget.installEventFilter(self)

    # 事件
    def eventFilter(self, watched, event):
        if watched != self.ui.videoWidget:
            return super(MainWindow, self).eventFilter(watched, event)
        # 鼠标事件
        if event.type() == QEvent.Type.MouseButtonPress:
            # 鼠标点击播放/暂停
            if event.button() == Qt.MouseButton.LeftButton:
                if self.player.state() == QMediaPlayer.State.PlayingState:
                    self.player.pause()
                else:
                    self.player.play()
        # 键盘事件
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                if self.ui.videoWidget.isFullScreen():
                    self.ui.videoWidget.setFullScreen(False)

        return super(MainWindow, self).eventFilter(watched, event)

    # 动作
    def open_act(self):
        self.player.setVideoOutput(self.ui.videoWidget)
        cap = "open video file"
        filt = "视频文件(*.wmv *.avi *.mp4 *.mov)"
        self.player.setMedia(QMediaContent(QFileDialog.getOpenFileUrl(caption=cap, filter=filt)[0]))
        self.play_video()

    # 按键功能
    def full_screen(self):
        if not self.ui.videoWidget.isFullScreen():
            self.ui.videoWidget.setFullScreen(True)

    def play_video(self):
        if self.player.state() != QMediaPlayer.State.PlayingState:
            self.player.play()

    def pause_video(self):
        if self.player.state() != QMediaPlayer.State.PausedState:
            self.player.pause()


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.ui.show()
    app.exec()
