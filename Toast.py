# standard
import sys
# pyqt
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import (QTimer, QPropertyAnimation, QRect, QPoint, QSize, Qt,
                          pyqtSignal)
from PyQt5.QtWidgets import (QFrame, QApplication, QVBoxLayout, QHBoxLayout, QStyle,
                             QLabel, QPushButton, QWidget, QDialog)


class Toaster(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # bootstrap
        self._bootstrap()
        # timer
        self.timer = QTimer(singleShot=True, timeout=self.hide)
        # stylesheet
        self.setStyleSheet('''
            Toaster {
                border: 1px solid #555;
                background-color: #333;
            }
        ''')

    def _bootstrap(self):
        self.setMaximumSize(380, 230)
        # general layout
        self.generalLayout = QVBoxLayout()
        self.setLayout(self.generalLayout)
        # customize window frame
        self.setWindowFlags(
            self.windowFlags() |
            Qt.FramelessWindowHint |
            Qt.BypassWindowManagerHint
        )
        self.notifLayout()
        self.messageBox()
        self.toastIcon()
        self.toastTitle()
        self.toastMessage()
        self.closeButton()

    def closeButton(self):
        self.btnClose = QPushButton('Dismiss')
        self.btnClose.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnClose.clicked.connect(self.close)
        self.generalLayout.addWidget(self.btnClose)
        self.btnClose.setStyleSheet("""
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

    def notifLayout(self):
        self.boxLayout = QHBoxLayout()
        self.boxLayout.setContentsMargins(0, 0, 0, 0)

    def messageBox(self):
        self.messageLayout = QVBoxLayout()
        self.boxLayout.addLayout(self.messageLayout)

    def toastIcon(self):
        self.toastIconLayout = QVBoxLayout()
        self.boxLayout.addLayout(self.toastIconLayout)

    def toastTitle(self):
        self.toastTitleLayout = QHBoxLayout()
        self.messageLayout.addLayout(self.toastTitleLayout)

    def toastMessage(self):
        self.toastMessageLayout = QHBoxLayout()
        self.messageLayout.addLayout(self.toastMessageLayout)

    def opacityEffect(self):
        self.opacityAni = QPropertyAnimation(self, b'windowOpacity')
        self.opacityAni.setStartValue(0.)
        self.opacityAni.setEndValue(1.)
        self.opacityAni.setDuration(200)
        self.opacityAni.start()
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
    def showMessage(timeout=5000):

        self = Toaster(None)
        # This is a dirty hack!
        # parentless objects are garbage collected, so the widget will be
        # deleted as soon as the function that calls it returns, but if an
        # object is referenced to *any* other object it will not, at least
        # for PyQt (I didn't test it to a deeper level)
        self.__self = self
        currentScreen = QApplication.primaryScreen()
        reference = QRect(
                QCursor.pos() - QPoint(1, 1),
                QSize(3, 3)
        )
        maxArea = 0
        for screen in QApplication.screens():
            intersected = screen.geometry().intersected(reference)
            area = intersected.width() * intersected.height()
            if area > maxArea:
                maxArea = area
                currentScreen = screen
        parentRect = currentScreen.availableGeometry()

        self.timer.setInterval(timeout)

        self.timer.start()
        # raise the widget and adjust its size to the minimum
        self.raise_()
        # self.adjustSize()
        margin = 10
        geo = self.geometry()
        # now the widget should have the correct size hints, let's move it to the
        # right place
        geo.moveBottomRight(parentRect.bottomRight() + QPoint(-margin, -margin))
        self.setGeometry(geo)
        self.show()
        self.opacityEffect()


class ShowButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generalLayout = QVBoxLayout(self)
        self.clickBtn = QPushButton('Click')
        self.clickBtn.clicked.connect(self.showButton)
        # attach
        self.generalLayout.addWidget(self.clickBtn)

    def showButton(self):
        self.rcWin = ShowNotif('salam', 'Boq')


class ShowNotif(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # bootstrap
        self._bootstrap()
        # location
        self.location()
        # stylesheet
        self.setStyleSheet("""
            ShowNotif {
                border: 1px solid #555;
                background-color: #333;
            }
        """)

    def _bootstrap(self):
        self.setFixedSize(380, 240)
        self.generalLayout = QHBoxLayout()
        self.generalLayout.setContentsMargins(0, 0, 0, 0)
        self.generalLayout.addStretch(1)
        self.setLayout(self.generalLayout)
        self.setWindowFlags(
            self.windowFlags() |
            Qt.FramelessWindowHint |
            Qt.BypassWindowManagerHint
        )
        self.closeButton()
        self.timerStart(5000)
        self.opacityEffect()

    def location(self, margin=10):
        # set location to bottom right
        currentScreen = QApplication.primaryScreen()
        reference = QRect(QCursor.pos() - QPoint(1, 1), QSize(3, 3))
        maxArea = 0
        for screen in QApplication.screens():
            intersected = screen.geometry().intersected(reference)
            area = intersected.width() * intersected.height()
            if area > maxArea:
                maxArea = area
                currentScreen = screen
        parentRect = currentScreen.availableGeometry()
        geo = self.geometry()
        geo.moveBottomRight(parentRect.bottomRight() + QPoint(-margin, -margin))
        self.setGeometry(geo)

    def closeButton(self):
        self.btnCloseLayout = QVBoxLayout()
        self.btnClose = QPushButton('X')
        self.btnClose.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnClose.clicked.connect(self.close)
        self.btnCloseLayout.addWidget(self.btnClose)
        self.generalLayout.addLayout(self.btnCloseLayout)
        self.btnCloseLayout.addStretch(1)
        self.btnClose.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border: none;
                color: #ccc;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                color: #999;
                background: #555;
            }
        """)

    def timerStart(self, timeout):
        self.timer = QTimer(singleShot=True, timeout=self.hide)
        self.timer.setInterval(timeout)
        self.timer.start()

    def opacityEffect(self):
        self.opacityAni = QPropertyAnimation(self, b'windowOpacity')
        self.opacityAni.setStartValue(0.)
        self.opacityAni.setEndValue(1.)
        self.opacityAni.setDuration(200)
        self.opacityAni.start()
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ShowNotif()
    main.show()
    sys.exit(app.exec_())
