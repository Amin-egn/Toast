# standard
import sys
# pyqt
from PyQt5 import QtCore, QtWidgets, QtGui


class QToaster(QtWidgets.QFrame):
    closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QToaster, self).__init__(*args, **kwargs)
        QtWidgets.QVBoxLayout(self)

        # self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
        #                    QtWidgets.QSizePolicy.Maximum)
        self.setFixedSize(350, 200)
        self.setStyleSheet('''
            QToaster {
                border: 1px solid #555;
                background-color: #333;
            }
        ''')
        # alternatively:
        # self.setAutoFillBackground(True)
        # self.setFrameShape(self.Box)

        self.timer = QtCore.QTimer(singleShot=True, timeout=self.hide)

        self.opacityAni = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.opacityAni.setStartValue(0.)
        self.opacityAni.setEndValue(1.)
        self.opacityAni.setDuration(100)
        self.opacityAni.finished.connect(self.checkClosed)

    def checkClosed(self):
        # if we have been fading out, we're closing the notification
        if self.opacityAni.direction() == self.opacityAni.Backward:
            self.close()

    def restore(self):
        # this is a "helper function", that can be called from mouseEnterEvent
        # and when the parent widget is resized. We will not close the
        # notification if the mouse is in or the parent is resized
        self.timer.stop()
        # also, stop the animation if it's fading out...
        self.opacityAni.stop()
        # ...and restore the opacity
        if self.parent():
            self.opacityEffect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    def hide(self):
        # start hiding
        self.opacityAni.setDirection(self.opacityAni.Backward)
        self.opacityAni.setDuration(1000)
        self.opacityAni.start()

    def enterEvent(self, event):
        self.restore()

    def leaveEvent(self, event):
        self.timer.start()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.deleteLater()

    @staticmethod
    def showMessage(message, title, level, closable=True, timeout=5000):

        self = QToaster(None)
        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.BypassWindowManagerHint
        )
        # This is a dirty hack!
        # parentless objects are garbage collected, so the widget will be
        # deleted as soon as the function that calls it returns, but if an
        # object is referenced to *any* other object it will not, at least
        # for PyQt (I didn't test it to a deeper level)
        self.__self = self
        currentScreen = QtWidgets.QApplication.primaryScreen()
        reference = QtCore.QRect(
                QtGui.QCursor.pos() - QtCore.QPoint(1, 1),
                QtCore.QSize(3, 3)
        )
        maxArea = 0
        for screen in QtWidgets.QApplication.screens():
            intersected = screen.geometry().intersected(reference)
            area = intersected.width() * intersected.height()
            if area > maxArea:
                maxArea = area
                currentScreen = screen
        parentRect = currentScreen.availableGeometry()

        self.timer.setInterval(timeout)
        # set icon
        if level == 1:
            pix = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning
        elif level == 2:
            pix = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical
        else:
            pix = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation

        # upper close button layout
        nofitLayout = QtWidgets.QHBoxLayout()
        # - level icon layout
        levelLayout = QtWidgets.QVBoxLayout()
        # - message box layout
        messageBoxLayout = QtWidgets.QVBoxLayout()
        # -- title layout
        titleLayout = QtWidgets.QHBoxLayout()
        # -- message layout
        messageLayout = QtWidgets.QHBoxLayout()
        # icon
        icon = self.style().standardIcon(pix)
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(icon.pixmap(32))
        levelLayout.addWidget(self.icon)
        # title
        self.ttl = QtWidgets.QLabel(title)
        self.ttl.setFixedSize(310, 30)
        self.ttl.setWordWrap(True)
        self.ttl.setStyleSheet("""
            QLabel{
                font: 16px Tahoma;
                font-weight: bold;
                color: white;
            }
        """)
        titleLayout.addWidget(self.ttl)
        # message
        self.msg = QtWidgets.QLabel(message)
        self.msg.setWordWrap(True)
        self.msg.setStyleSheet("""
            QLabel{
                color: #ddd;
                font: 12px Tahoma;
                font-weight: 100;
            }
        """)
        messageLayout.addWidget(self.msg)
        # attach
        messageBoxLayout.addLayout(titleLayout)
        messageBoxLayout.addLayout(messageLayout)
        nofitLayout.addLayout(levelLayout)
        nofitLayout.addLayout(messageBoxLayout)
        self.layout().addLayout(nofitLayout)

        if closable:
            self.closeButton = QtWidgets.QPushButton('Dismiss')
            self.layout().addWidget(self.closeButton)
            self.closeButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.closeButton.clicked.connect(self.close)
            self.closeButton.setStyleSheet("""
                QPushButton{
                    width: 50px;
                    height: 30px;
                    border: 1px solid #ccc;
                    background: #ddd;
                    font: 16px
                }
                QPushButton:hover{
                    background: #999
                }
            """)

        self.timer.start()
        # raise the widget and adjust its size to the minimum
        self.raise_()
        # self.adjustSize()
        margin = 10
        geo = self.geometry()
        # now the widget should have the correct size hints, let's move it to the
        # right place
        geo.moveBottomRight(parentRect.bottomRight() + QtCore.QPoint(-margin, -margin))
        self.setGeometry(geo)
        self.show()
        self.opacityAni.start()


class ShowNofit(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generalLayout = QtWidgets.QVBoxLayout(self)
        self.rcWin = None
        self.clickBtn = QtWidgets.QPushButton('Click')
        self.clickBtn.clicked.connect(self.showToaster)
        # attach
        self.generalLayout.addWidget(self.clickBtn)

    def showToaster(self):
        if self.rcWin is None:
            self.rcWin = QToaster()
        self.rcWin.showMessage('Thread: Style Sheets: re-using referencing builtin', 'Warning', 3)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = ShowNofit()
    main.show()
    sys.exit(app.exec_())
