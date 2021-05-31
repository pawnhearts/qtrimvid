#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from subprocess import Popen, PIPE
from typing import List, Union

from PyQt5.QtCore import QDir, Qt, QUrl, QTime
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSlider,
    QStyle,
    QVBoxLayout, QMessageBox,
)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from fire import Fire
from loguru import logger


class VideoWindow(QMainWindow):
    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle(
            "PyQt Video Player Widget Example - pythonprogramminglanguage.com"
        )

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionLabel = QLabel("")
        self.durationLabel = QLabel("")
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon("open.png"), "&Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip("Open movie")
        openAction.triggered.connect(self.openFile)


        self.trimFromButton = QPushButton()
        self.trimFromButton.setEnabled(False)
        self.trimFromButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.trimFromButton.setText('Trim from here')
        self.trimFromButton.clicked.connect(self.trimFrom)

        trimFromAction = QAction(QIcon("start.png"), "&Trim from here", self)
        trimFromAction.setShortcut("Ctrl+s")
        trimFromAction.setStatusTip("Trim from here")
        trimFromAction.triggered.connect(self.trimFrom)

        self.trimToButton = QPushButton()
        self.trimToButton.setEnabled(False)
        self.trimToButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.trimToButton.setText('Trim to here')
        self.trimToButton.clicked.connect(self.trimTo)
        
        trimToAction = QAction(QIcon("end.png"), "Trim to her&e", self)
        trimToAction.setShortcut("Ctrl+e")
        trimToAction.setStatusTip("Trim to here")
        trimToAction.triggered.connect(self.trimTo)

        # Create exit action
        exitAction = QAction(QIcon("exit.png"), "&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        # fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(trimFromAction)
        fileMenu.addAction(trimToAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionLabel)
        controlLayout.addWidget(self.trimFromButton)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.trimToButton)
        controlLayout.addWidget(self.durationLabel)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self, fileNames: Union[List[Path], Path]):
        if not fileNames:
            fileNames, _ = QFileDialog.getOpenFileNames(
                self, "Open Movie", QDir.homePath()
            )

        if fileNames:
            if not isinstance(fileNames, list):
                fileNames = [fileNames]
            self.mediaPlayer.stop()
            self.playlist = QMediaPlaylist()
            for fileName in fileNames:
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playlist.setCurrentIndex(0)
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.mediaPlayer.setPlaylist(self.playlist)
            self.playButton.setEnabled(True)
            self.trimToButton.setEnabled(True)
            self.trimFromButton.setEnabled(True)
            self.play()

    def exitCall(self):
        sys.exit(app.exec_())

    def trim(self, path, ss=0, t=None):
        print(ss)
        tmp_path = f"{path}.tmp{os.path.splitext(path)[1]}"
        # p = wProcess()
        p = Popen(
            [
                "ffmpeg",
                "-y",
                "-i",
                path,
                "-ss",
                str(ss),
                *(["-t", str(t)] if t is not None else []),
                "-vcodec",
                "copy",
                "-acodec",
                "copy",
                tmp_path,
            ], stderr=PIPE, stdout=PIPE
        )

        if p.wait() == 0:
            logger.info(p.stdout.read().decode())
            os.rename(tmp_path, path)
            self.openFile(path)
        else:
            err_text = p.stderr.read().decode()
            logger.error(err_text)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText(err_text)
            msg.setWindowTitle("Error")
            msg.exec_()
            os.unlink(tmp_path)

    def trimFrom(self):
        p = int(self.mediaPlayer.position() / 1000)
        self.trim(
            self.mediaPlayer.currentMedia()
            .canonicalUrl()
            .toString()
            .replace("file://", ""),
            ss=p,
        )

    def trimTo(self):
        p = int(self.mediaPlayer.position() / 1000)
        self.trim(
            self.mediaPlayer.currentMedia()
            .canonicalUrl()
            .toString()
            .replace("file://", ""),
            ss=0,
            t=p,
        )

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.positionLabel.setText(
            QTime(
                int((position / 3600000)) % 24,
                int((position / 60000)) % 60,
                int((position / 1000)) % 60
                ).toString()
        )

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        self.durationLabel.setText(f"{duration/1000}")
        self.durationLabel.setText(
            QTime(
                int((duration / 3600000)) % 24,
                int((duration / 60000)) % 60,
                int((duration / 1000)) % 60,
            ).toString()
        )

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.trimToButton.setEnabled(False)
        self.trimFromButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())


app = QApplication(sys.argv)


def main(*path: List[Path]):
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    if path:
        player.openFile(path)
    sys.exit(app.exec_())


if __name__ == "__main__":
    Fire(main)
