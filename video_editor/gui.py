from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtCore import Qt, QUrl, QSize, QFileInfo
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *

from video_editor.editor import VideoEditor
import threading
import os
import time
import shutil
import subprocess



class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self.videoPath = None
        self.videoTmpPath = None
        self.videoDuration = None
        self.videoEditor = None

        # Font
        # self.setFont(QFont("Noto Sans", 10))

        # Edit window
        self.editWindow = EditWidget(self)

        # Video widget and media player
        videoWidget = QVideoWidget()
        videoWidget.setStyleSheet('background: black')
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        # Play button
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(26)

        self.playButton.setIconSize(QSize(10, 10))
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.togglePlay)

        # Time slider
        self.positionSlider = QSliderMarker(Qt.Horizontal)

        # self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Time label
        self.timeLabel = QLabel("- -:- -. - -")
        # self.timeLabel.setAlignment(Qt.AlignTop)
        self.timeLabel.setAlignment(Qt.AlignBottom)
        self.timeLabel.setFixedHeight(24)

        # Open button
        openButton = QPushButton("Open")
        openButton.setFixedHeight(24)
        openButton.clicked.connect(self.loadVideoFile)

        # Open Folder button
        self.openFolderButton = QPushButton("打开文件夹")
        self.openFolderButton.setEnabled(False)
        self.openFolderButton.setFixedHeight(24)
        self.openFolderButton.clicked.connect(self.openFolder)

        # Split button
        self.splitButton = QPushButton("分割")
        self.splitButton.setToolTip("对当前时间点的位置进行分割")
        self.splitButton.setEnabled(False)
        self.splitButton.setFixedHeight(24)
        self.splitButton.clicked.connect(self.split)

        # Export selected button
        # self.exportAllButton = QPushButton("Export selected splits")
        # self.exportAllButton.setToolTip("Join all selected splits in a single video file")
        # self.exportAllButton.setEnabled(False)
        # self.exportAllButton.setFixedHeight(24)
        # self.exportAllButton.clicked.connect(self.exportVideo)

        # Export Audio button
        self.exportAudioButton = QPushButton("提取音频MP3")
        self.exportAudioButton.setToolTip("提取整段视频文件的音频导出为MP3")
        self.exportAudioButton.setEnabled(False)
        self.exportAudioButton.setFixedHeight(24)
        self.exportAudioButton.clicked.connect(self.exportAuido)

        # Export JPG button
        self.exportJPGButton = QPushButton("当前画面截取JPG")
        self.exportJPGButton.setToolTip("将当前时间点的画面保存为")
        self.exportJPGButton.setEnabled(False)
        self.exportJPGButton.setFixedHeight(24)
        # print(self.mediaPlayer.position())
        self.exportJPGButton.clicked.connect(self.exportJPG)

        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.setFixedHeight(24)
        self.statusBar.showMessage("请直接将视频文件拖入窗口")

        # Controls layout [open, play and slider]
        # sliderLayout = QHBoxLayout()

        timeLayout = QHBoxLayout()
        timeLayout.setContentsMargins(0, 0, 0, 0)
        timeLayout.addWidget(self.playButton)
        timeLayout.addStretch(1)  # 增加伸缩量
        # timeLayout.addWidget(openButton)
        # timeLayout.addStretch(1)  # 增加伸缩量
        timeLayout.addWidget(self.timeLabel)

        # Controls layout [open, play and slider]
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.splitButton)
        controlLayout.addWidget(self.positionSlider)

        # Editor layout [split and export_all]
        editorLayout = QHBoxLayout()
        editorLayout.setContentsMargins(0, 0, 0, 0)
        editorLayout.addWidget(self.openFolderButton)
        editorLayout.addStretch(50)  # 增加伸缩量

        editorLayout.addWidget(self.exportJPGButton)
        editorLayout.addWidget(self.exportAudioButton)
        # editorLayout.addWidget(self.exportAllButton)

        editorLayout.addStretch(1)

        # Splits layout
        self.splitsLayout = QHBoxLayout()
        self.splitsLayout.setContentsMargins(0, 0, 0, 0)
        self.splitsLayout.setSpacing(0)

        # General layout
        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(timeLayout)
        layout.addLayout(controlLayout)

        layout.addLayout(self.splitsLayout)
        layout.addLayout(editorLayout)
        layout.addWidget(self.statusBar)
        self.setLayout(layout)

    @staticmethod
    def positionToString(position):
        seconds = position // 1000
        return "{:02d}:{:02d}.{:02d}".format(seconds // 60, seconds % 60, position % 1000 // 10)

    def openEditWindow(self, splitId):
        config = self.videoEditor.get_split_config(splitId)
        self.editWindow.updateFields(splitId, config)
        self.editWindow.show()


    def openFolder(self):
        if os.path.exists(os.path.dirname(self.videoPath)):
            subprocess.Popen('open %s' % os.path.dirname(self.videoPath), shell=True)


    def loadVideoFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose video file", ".",
                                                  "Video Files (*.mp4 *.flv *.ts *.mkv *.avi)")
        self.videoTmpPath = copy_tmp_file(fileName)
        if fileName != '':
            self.videoPath = fileName
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.videoTmpPath)))
            self.playButton.setEnabled(True)
            self.splitButton.setEnabled(True)
            self.exportJPGButton.setEnabled(True)
            self.exportAudioButton.setEnabled(True)
            self.openFolderButton.setEnabled(True)
            # self.exportAllButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            self.positionSlider.update()
            self.togglePlay()
            self.mediaPlayer.pause()


    def dragEnterEvent(self, event):  # 拖动开始时，以及刚进入目标控件时调用
        event.acceptProposedAction()  # 必须要有

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            print(urls)
            try:
                url = urls[0]
                fileName = str(url.toLocalFile())
                self.videoTmpPath = copy_tmp_file(fileName)

                if fileName:
                    self.videoPath = fileName
                    self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.videoTmpPath)))
                    self.playButton.setEnabled(True)
                    self.splitButton.setEnabled(True)
                    self.exportAudioButton.setEnabled(True)
                    self.exportJPGButton.setEnabled(True)
                    self.openFolderButton.setEnabled(True)
                    # self.exportAllButton.setEnabled(True)
                    self.statusBar.showMessage(fileName)
                    self.positionSlider.update()
                    self.togglePlay()
                    self.mediaPlayer.pause()
                    self.updateSplitsGUI()

            except:
                pass
        else:
            super(VideoPlayer, self).dropEvent(event)

    def getSplitWidgets(self):
        for i in range(self.splitsLayout.count()):
            yield self.splitsLayout.itemAt(i).widget()

    def updateSplitsGUI(self):
        oldWidgets = list(self.getSplitWidgets())

        splitTimes = []
        for i, split in enumerate(self.videoEditor.get_splits()):
            splitWgt = SplitWidget(self, i, split)
            splitWgt.setToolTip("{} - {}".format(self.positionToString(split.start_time),
                                                 self.positionToString(split.end_time)))
            splitWgt.setMinimumWidth(4)
            self.splitsLayout.addWidget(splitWgt, split.duration)
            splitTimes.append(split.start_time)

        for widget in oldWidgets:
            widget.setParent(None)

        self.positionSlider.splitValues = splitTimes
        self.positionSlider.update()

    def exportVideo(self):
        splitIds = []
        for splitWgt in self.getSplitWidgets():
            if splitWgt.marked:
                splitIds.append(splitWgt.splitId)

        if not splitIds:
            QMessageBox(QMessageBox.NoIcon, "No selected splits",
                        "You have to select at least one split to export a video", QMessageBox.NoButton, self).show()
            return

        videoExtension = self.videoPath.split(".")[-1]
        fileName, _ = QFileDialog.getSaveFileName(self, "Choose video file", ".",
                                                  "Video Files (*.{})".format(videoExtension))
        if fileName:
            t = threading.Thread(target=self.generateVideo, args=(splitIds, fileName))
            t.setDaemon(True)
            t.start()
            QMessageBox(fileName, self).show()

    def exportAuido(self):
        OutName = os.path.splitext(self.videoPath)[0] + str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '.mp3'
        if OutName:
            t = threading.Thread(target=self.generateAudio, args=(OutName,))
            t.setDaemon(True)
            t.start()
            QMessageBox.information(self, '', '提取音频导出路径为:\n%s' % OutName)

    def exportJPG(self):
        OutName = os.path.splitext(self.videoPath)[0] + str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '.jpg'
        print(self.mediaPlayer.position())
        if OutName:
            t = threading.Thread(target=self.generateJPG, args=(OutName, self.mediaPlayer.position(),))
            t.setDaemon(True)
            t.start()
            QMessageBox.information(self, '', '提取的图片路径为:\n%s' % OutName)

    def generateVideo(self, splitIds, OutName):
        self.setDisabled(True)
        self.mediaPlayer.pause()
        self.videoEditor.export_and_join_splits(splitIds, OutName)
        self.setDisabled(False)

    def generateAudio(self, OutName):
        self.setDisabled(True)
        self.mediaPlayer.pause()
        self.videoEditor.export_audio(OutName)
        self.setDisabled(False)

    def generateJPG(self, OutName, position):
        self.setDisabled(True)
        self.mediaPlayer.pause()
        self.videoEditor.export_jpg(OutName, position)
        self.setDisabled(False)

    def togglePlay(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def topause(self):
        self.mediaPlayer.pause()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        # Media player positionChanged event, updates slider and timer
        self.positionSlider.setValue(position)
        self.timeLabel.setText(self.positionToString(position))

    def durationChanged(self, duration):
        # Triggers when a video is loaded
        self.positionSlider.setRange(0, duration)
        self.timeLabel.setText("00:00:00")
        self.videoDuration = duration
        self.videoEditor = VideoEditor(self.videoTmpPath, self.videoDuration, self.videoPath)
        self.updateSplitsGUI()

    def setPosition(self, position):
        # Slider setPosition event, updates media player and timer
        self.mediaPlayer.setPosition(position)
        self.timeLabel.setText(self.positionToString(position))
        # if position < self.positionSlider.maximum() and self.mediaPlayer.state() != QMediaPlayer.PlayingState:
        #     self.mediaPlayer.play()
        # self.updateSplitsGUI()

    def split(self):
        self.topause()
        time = self.positionSlider.value()
        self.videoEditor.add_split(time)
        self.updateSplitsGUI()
        # self.positionSlider.update()

    def handleError(self):
        self.playButton.setEnabled(False)
        self.splitButton.setEnabled(False)
        # self.exportAllButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())


class QSliderMarker(QSlider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.splitValues = []

    def mousePressEvent(self, ev):
        newPosition = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width())
        self.setSliderPosition(newPosition)
        self.parent().setPosition(newPosition)
        self.parent().topause()

    def mouseMoveEvent(self, ev):
        newPosition = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width())
        self.setSliderPosition(newPosition)
        self.parent().setPosition(newPosition)
        self.parent().topause()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.maximum() == 0:
            return

        painter = QPainter(self)
        for val in self.splitValues:
            percent = val / self.maximum()
            px = percent * self.width()
            painter.drawLine(px, 1, px, 200)


class SplitWidget(QPushButton):

    def __init__(self, parent, splitId, split):
        super().__init__(parent)
        self.marked = False
        self.textOptions = ['✗', '✓']
        self.splitId = splitId
        self.split = split
        self.toggleMark()

    def toggleMark(self):
        self.marked ^= True
        # newText = self.textOptions[int(self.marked)]
        newText = self.split.get_split_time()
        self.setText(newText)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        rightMerge, leftMerge = object(), object()
        if self.splitId < self.parent().splitsLayout.count() - 1:
            rightMerge = menu.addAction("合并→→→")
        if self.splitId > 0:
            leftMerge = menu.addAction("←←←合并")
        # mark = menu.addAction("Unselect" if self.marked else "Select")
        # edit = menu.addAction("Edit")
        webp = menu.addAction("导出Webp")
        gif = menu.addAction("导出GIF")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == rightMerge:
            self.parent().videoEditor.merge_split_with_next(self.splitId)
            self.parent().updateSplitsGUI()
        elif action == leftMerge:
            self.parent().videoEditor.merge_split_with_previous(self.splitId)
            self.parent().updateSplitsGUI()
        if action == webp:
            # videoExtension = self.parent().videoPath.split(".")[-1]
            # fileName, _ = QFileDialog.getSaveFileName(self, "Choose video file", ".",
            #                                           "Video Files (*.{})".format('webp'))
            # fileName = os.path.splitext(self.parent().videoEditor.video_path)[0] + \
            #            str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '.webp'
            # if fileName:
            t = threading.Thread(target=self.exportWebp)
            t.setDaemon(True)
            t.start()
        if action == gif:
            # videoExtension = self.parent().videoPath.split(".")[-1]
            # fileName, _ = QFileDialog.getSaveFileName(self, "Choose video file", ".",
            #                                           "Video Files (*.{})".format('webp'))
            # fileName = os.path.splitext(self.parent().videoEditor.video_path)[0] + \
            #            str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '.gif'
            # if fileName:
            t = threading.Thread(target=self.exportGif)
            t.setDaemon(True)
            t.start()

        # elif action == mark:
        #     self.toggleMark()
        # elif action == edit:
        #     self.parent().openEditWindow(self.splitId)

    def exportWebp(self):
        self.setDisabled(True)
        self.setText('⌛')
        self.parent().videoEditor.export_split_webp(self.splitId)
        # textStatus = self.textOptions[int(self.marked)]
        self.setText('Webp导出完成')
        time.sleep(3)
        self.setText(self.split.get_split_time())
        self.setDisabled(False)

    def exportGif(self):
        self.setDisabled(True)
        self.setText('⌛')
        self.parent().videoEditor.export_split_gif(self.splitId)
        # textStatus = self.textOptions[int(self.marked)]
        self.setText('Gif导出完成')
        time.sleep(3)
        self.setText(self.split.get_split_time())
        self.setDisabled(False)


class EditWidget(QDialog):

    def __init__(self, parent):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Edit split")
        self.splitId = None

        # Reencode layout
        self.reencodeCheckbox = QCheckBox("Reencode")
        self.reencodeCheckbox.setToolTip("Check this option to have more accurate cuts and avoid black "
                                         "frames at the end and beginning of the split")

        reencodeLayout = QVBoxLayout()
        reencodeLayout.setContentsMargins(0, 0, 0, 0)
        reencodeLayout.addWidget(self.reencodeCheckbox)

        # Compress layout
        self.compressCheckbox = QCheckBox("Compress")
        self.compressCheckbox.setToolTip("Check this option to compress video and audio quality "
                                         "and reduce the output file size")

        compressLayout = QVBoxLayout()
        compressLayout.setContentsMargins(0, 0, 0, 0)
        compressLayout.addWidget(self.compressCheckbox)

        # Audio layout
        self.removeAudioCheckbox = QCheckBox("Remove audio")
        self.removeAudioCheckbox.setToolTip("Check this option to delete audio")

        audioLayout = QVBoxLayout()
        audioLayout.setContentsMargins(0, 0, 0, 0)
        audioLayout.addWidget(self.removeAudioCheckbox)

        # Speedup layout
        self.speedupCheckbox = QCheckBox("Speed up/down")
        self.speedupCheckbox.setToolTip("Accelerate or decelerate video and audio speed")

        speedupLayoutOpt1 = QHBoxLayout()
        self.speedupFactor = QDoubleSpinBox()
        self.speedupFactor.setValue(1)
        self.speedupFactor.setMinimum(0)
        factorLabel = QLabel("Factor:")
        factorLabel.setToolTip("Increase or decrease video speed with this factor")
        speedupLayoutOpt1.addItem(QSpacerItem(25, 0, QSizePolicy.Minimum, QSizePolicy.Minimum))
        speedupLayoutOpt1.addWidget(factorLabel)
        speedupLayoutOpt1.addWidget(self.speedupFactor)

        speedupLayoutOpt2 = QHBoxLayout()
        self.keepFramesCheckbox = QCheckBox("Keep all frames")
        self.keepFramesCheckbox.setDisabled(True)
        speedupLayoutOpt2.addItem(QSpacerItem(25, 0, QSizePolicy.Minimum, QSizePolicy.Minimum))
        speedupLayoutOpt2.addWidget(self.keepFramesCheckbox)

        speedupLayout = QVBoxLayout()
        speedupLayout.setContentsMargins(0, 0, 0, 0)
        speedupLayout.addWidget(self.speedupCheckbox)
        speedupLayout.addLayout(speedupLayoutOpt1)
        speedupLayout.addLayout(speedupLayoutOpt2)

        # General layout
        layout = QVBoxLayout()
        layout.addLayout(reencodeLayout)
        layout.addLayout(compressLayout)
        layout.addLayout(audioLayout)
        layout.addLayout(speedupLayout)
        self.setLayout(layout)

    def updateFields(self, splitId, config):
        self.splitId = splitId
        self.reencodeCheckbox.setChecked(config.get('reencode', False))
        self.compressCheckbox.setChecked(config.get('compress', False))
        self.removeAudioCheckbox.setChecked(config.get('removeaudio', False))
        speedupSettings = config.get('speedup')
        if speedupSettings:
            self.speedupCheckbox.setChecked(True)
            self.speedupFactor.setValue(config['speedup'].get('factor', 1))
            self.keepFramesCheckbox.setChecked(not config['speedup'].get('dropframes', True))
        else:
            self.speedupCheckbox.setChecked(False)
            self.speedupFactor.setValue(1)
            self.keepFramesCheckbox.setChecked(False)

    def getSplitConfig(self):
        speedup = False
        if self.speedupCheckbox.isChecked():
            speedup = {
                'factor': self.speedupFactor.value(),
                'dropframes': not self.keepFramesCheckbox.isChecked(),
            }

        return {
            'reencode': self.reencodeCheckbox.isChecked(),
            'compress': self.compressCheckbox.isChecked(),
            'removeaudio': self.removeAudioCheckbox.isChecked(),
            'speedup': speedup
        }

    def saveConfig(self):
        config = self.getSplitConfig()
        self.parent().videoEditor.update_split(self.splitId, config)

    def reject(self):
        self.saveConfig()
        super().reject()


def copy_tmp_file(file_path):
    dir =os.path.dirname(sys.executable)
    # dir = os.path.dirname(os.path.abspath(__file__))
    tmp_folder = os.path.join(dir, 'tmp')
    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)
    else:
        shutil.rmtree(tmp_folder)
        os.mkdir(tmp_folder)

    suffix = os.path.splitext(file_path)[1]
    tmp_file = os.path.join(tmp_folder, 'temporary' + suffix)
    shutil.copyfile(file_path, tmp_file)
    print(tmp_file)
    while os.path.exists(tmp_file):
        return tmp_file

def open_interface():
    import sys

    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)

    sys.excepthook = except_hook

    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Video Split tool")
    player.resize(1000, 600)
    player.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    open_interface()
