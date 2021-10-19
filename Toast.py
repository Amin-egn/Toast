# standard
import sys
from functools import partial
# pyqt
from PyQt5.QtGui import (QCursor, QIcon, QPixmap, QFont)
from PyQt5.QtCore import (QTimer, QPropertyAnimation, QRect, QPoint, QSize, Qt,
                          pyqtSignal, QThread, QObject)
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QStyle,
                             QLabel, QPushButton, QWidget, QDialog)


class Toaster(QDialog):
    closed = pyqtSignal(int)

    def __init__(self, tid, title, message, timeout, margin, parent=None):
        super().__init__(parent)
        self._id = tid
        self.title = title
        self.message = message
        self.timeout = timeout
        self.margin = margin
        # bootstrap
        self._bootstrap()
        # location
        self._location(self.margin)
        # stylesheet
        self.setStyleSheet("""
            Toaster {
                background-color: #2d2d2d;
            }
            #Title {
                color: #ffffff;
            }
            #Message {
                color: #a5a5a5;
            }
        """)

    def _bootstrap(self):
        self.setWindowModality(Qt.NonModal)
        self.setFixedSize(380, 220)
        self.generalLayout = QHBoxLayout()
        self.generalLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.generalLayout)
        self.setWindowFlags(
            self.windowFlags() |
            Qt.FramelessWindowHint |
            Qt.BypassWindowManagerHint
        )
        self.iconBar()
        self.messageBar(self.title, self.message)
        self.closeButton()
        self.timerStart(self.timeout)
        self.opacityEffect()

    def closeButton(self):
        self.btnCloseLayout = QVBoxLayout()
        self.btnClose = QPushButton('X')
        self.btnClose.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnClose.clicked.connect(self.close)
        self.btnCloseLayout.addWidget(self.btnClose)
        self.generalLayout.addLayout(self.btnCloseLayout)
        self.btnClose.setFixedSize(30, 30)
        self.btnCloseLayout.addStretch(1)
        self.btnClose.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border: none;
                color: #a2a2a2;
            }
            QPushButton:hover {
                color: #f1f1f1;
            }
        """)

    def messageBar(self, title, message):
        self.messageLayout = QVBoxLayout()
        self.messageLayout.setContentsMargins(0, 10, 0, 0)
        # title font
        fontTitle = QFont()
        fontTitle.setPointSize(18)
        fontTitle.setWeight(90)
        # message font
        fontMessage = QFont()
        fontMessage.setPointSize(12)
        fontMessage.setWeight(60)
        # title
        self.txtTitle = QLabel(title)
        self.txtTitle.setWordWrap(True)
        self.txtTitle.setFont(fontTitle)
        self.txtTitle.setObjectName('Title')
        # message
        self.txtMessage = QLabel(message)
        self.txtMessage.setWordWrap(True)
        self.txtMessage.setFont(fontMessage)
        self.txtMessage.setObjectName('Message')
        # attach
        self.messageLayout.addWidget(self.txtTitle)
        self.messageLayout.addWidget(self.txtMessage)
        self.messageLayout.addStretch(1)
        self.generalLayout.addLayout(self.messageLayout)

    def iconBar(self):
        self.iconLayout = QVBoxLayout()
        self.iconLayout.setContentsMargins(10, 0, 10, 0)
        self.lblIcon = QLabel('icon')
        self.pix = QPixmap(r'E:\Logo.png')
        self.lblIcon.setPixmap(self.pix)
        self.lblIcon.setScaledContents(True)
        self.lblIcon.setFixedSize(72, 72)
        self.iconLayout.addWidget(self.lblIcon)
        self.generalLayout.addLayout(self.iconLayout)

    def _location(self, margin):
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
        geo.moveBottomRight(parentRect.bottomRight() + QPoint(-10, -margin))
        self.setGeometry(geo)

    def timerStart(self, timeout):
        self.timer = QTimer(singleShot=True, timeout=self.hide)
        self.timer.setInterval(timeout)
        self.timer.start()

    def opacityEffect(self):
        self.opacityAni = QPropertyAnimation(self, b'windowOpacity')
        self.opacityAni.setStartValue(0.)
        self.opacityAni.setEndValue(1.)
        self.opacityAni.setDuration(300)
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
        self.closed.emit(self._id)

    def showToast(self):
        self.show()


class Observer(object):
    def __init__(self):
        self.toastList = list()

    def manager(self, title, message, timeout):
        nextID = len(self.toastList)
        margin = 10
        if len(self.toastList) == 0:
            margin = 10
        else:
            margin += 230
        self.notif = Toaster(nextID, title, message, timeout, margin)
        self.toastList.append(nextID)
        self.notif.closed.connect(self.endTimer)
        self.notif.showToast()

    def endTimer(self, index):
        self.toastList.remove(index)

_notifs = Observer()

show = _notifs.manager
