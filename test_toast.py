import Toast

import sys, time

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class ShowButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generalLayout = QVBoxLayout(self)
        self.clickBtn = QPushButton('Click')
        self.clickBtn.clicked.connect(self.showButton)
        # attach
        self.generalLayout.addWidget(self.clickBtn)

    def showButton(self):
        Toast.show('Salam', 'Salam Salam 100ta Salam', 5000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ShowButton()
    main.show()
    sys.exit(app.exec())
