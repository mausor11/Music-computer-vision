from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt

class CustomButton(QPushButton):
    def __init__(self, on_color, off_color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(45, 45)
        self.on_color = QColor(on_color)
        self.off_color = QColor(off_color)
        self.color = self.off_color
        self.setCheckable(True)
        self.clicked.connect(self.update_color)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def update_color(self):
        self.color = self.on_color if self.isChecked() else self.off_color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QColor(self.color))
        painter.drawEllipse(0, 0, 45, 45)

class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(115, 115)
        self.setStyleSheet("background:transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QGridLayout()
        layout.setContentsMargins(13, 13, 13, 13)
        layout.setSpacing(10)

        button1 = CustomButton("#4C75DD", "#3C414E")
        button2 = QPushButton()
        button2.clicked.connect(lambda: print("Voice Recognition"))
        button3 = QPushButton()
        button3.clicked.connect(lambda: print("Search Button"))
        button4 = CustomButton("#3C414E", "#B42E2E")

        for button in [button1, button2, button3, button4]:
            button.setFixedSize(45, 45)

        layout.addWidget(button1, 0, 0)
        layout.addWidget(button2, 0, 1)
        layout.addWidget(button3, 1, 0)
        layout.addWidget(button4, 1, 1)

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.white, 1))
        painter.drawRect(self.rect())

def main():
    app = QApplication([])
    widget = CustomWidget()
    widget.show()
    app.exec_()

if __name__ == "__main__":
    main()