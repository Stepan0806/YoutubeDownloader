import os
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QImage, QPixmap

from download import find_video, download
from main_window import Ui_MainWindow


class Runnable(QtCore.QRunnable):
    def __init__(self, target, args):
        super().__init__()
        self.target = target
        self.args = args

    def run(self):
        self.target(*self.args)


def run_thread(target, args=tuple()):
    pool = QtCore.QThreadPool.globalInstance()
    runnable = Runnable(target, args)
    pool.start(runnable)


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.thumbnail = QImage('img/Youtube.png')
        self.streams = {}
        self.showMaximized()
        self.url_input.returnPressed.connect(lambda: run_thread(self.find_video))
        self.save_button.pressed.connect(self.save)

    def find_video(self):
        self.video_title.setText('Please wait...')
        title, thumbnail_data, self.streams = find_video(self.url_input.text())
        self.video_title.setText(title)

        if thumbnail_data:
            self.thumbnail = QImage()
            self.thumbnail.loadFromData(thumbnail_data)
        else:
            self.thumbnail = QImage('img/Youtube.png')
        self.resizeEvent(None)

        self.download_choose.clear()
        for stream_info in self.streams.keys():
            self.download_choose.addItem(stream_info)
        self.download_choose.setCurrentIndex(0)

    def save(self):
        download_choose = self.download_choose.currentText()
        if download_choose == '':
            return
        title = self.video_title.text()
        path = self.get_save_path(download_choose, title)
        if not path:
            return

        def thread():
            self.file_name_label.setText(path[-1])
            self.video_title.setText('Downloading...')
            result = download(self.streams[download_choose], path)
            if result != 'done':
                self.video_title.setText(result)
            else:
                self.video_title.setText(title)

        run_thread(thread)

    def get_save_path(self, download_choose, title):
        directory = os.path.join(os.path.expanduser('~'), 'Videos', title)
        filter = ' '.join(download_choose.split()[-2:])
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'YoutubeDownloader', directory, filter)[0]
        if not path:
            return
        true_extension = filter.split('.')[-1][:-1]
        path = '.'.join([path.split('.')[0], true_extension])
        return os.path.split(path)

    def resizeEvent(self, event):
        size = self.video_thumbnail.size()
        pixmap = QPixmap(self.thumbnail).scaled(size.width(), size.height(), QtCore.Qt.KeepAspectRatio)
        self.video_thumbnail.setPixmap(pixmap)
        if event is not None:
            QtWidgets.QMainWindow.resizeEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
