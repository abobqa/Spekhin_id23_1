import math
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QWidget


class CircularAnimationWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Circle Animation")
        self.setGeometry(100, 100, 600, 600)
        self.circle_radius = 200
        self.current_angle = -90

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.refresh_position)
        self.animation_timer.start(5)

    def refresh_position(self):
        self.current_angle -= 0.2
        if self.current_angle <= -360:
            self.current_angle += 360
        self.update()

    def paintEvent(self, event):
        canvas = QPainter(self)
        canvas.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        canvas.setPen(QColor(228, 0, 100))
        canvas.drawEllipse(center_x - self.circle_radius, center_y - self.circle_radius, self.circle_radius * 2, self.circle_radius * 2)

        pos_x = center_x + self.circle_radius * math.cos(math.radians(self.current_angle))
        pos_y = center_y + self.circle_radius * math.sin(math.radians(self.current_angle))
        canvas.drawEllipse(int(pos_x) - 5, int(pos_y) - 5, 10, 10)


app = QApplication([])
widget = CircularAnimationWidget()
widget.show()
app.exec()
