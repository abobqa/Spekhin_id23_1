import sys
import random
import math
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget


class Goat:
    def __init__(self, x, y, size=20, fertility=0.2, endurance=0.1):
        self.x = x
        self.y = y
        self.size = size
        self.fertility = fertility  # Плодотворность (увеличение размера после еды)
        self.endurance = endurance  # Выносливость (уменьшение размера при голоде)
        self.is_eating = False

    def move_towards(self, cabbage_x, cabbage_y, speed=5):
        dx = cabbage_x - self.x
        dy = cabbage_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 1:
            self.x += dx / distance * speed
            self.y += dy / distance * speed

    def eat_cabbage(self):
        self.size += self.fertility
        self.is_eating = True

    def hunger(self):
        self.size -= self.endurance
        if self.size < 5:
            self.size = 5


class Cabbage:
    def __init__(self, x, y, size=15):
        self.x = x
        self.y = y
        self.size = size


class Field(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.goat_herd = [Goat(200, 200)]  # Стадо коз
        self.cabbages = [Cabbage(random.randint(50, 350), random.randint(50, 350)) for _ in range(5)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_field)
        self.timer.start(50)

    def initUI(self):
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle('Goats and Cabbages')
        self.show()

    def update_field(self):
        if len(self.cabbages) > 0:
            nearest_cabbage = self.find_nearest_cabbage()
            for goat in self.goat_herd:
                goat.move_towards(nearest_cabbage.x, nearest_cabbage.y)
                distance = math.sqrt((goat.x - nearest_cabbage.x) ** 2 + (goat.y - nearest_cabbage.y) ** 2)
                if distance < 10:
                    goat.eat_cabbage()
                    nearest_cabbage.size -= 1  # Уменьшение размера капусты
                    if nearest_cabbage.size <= 0:
                        self.cabbages.remove(nearest_cabbage)
        else:
            for goat in self.goat_herd:
                goat.hunger()

        for goat in self.goat_herd:
            if goat.is_eating and nearest_cabbage.size <= 0:
                goat.is_eating = False

        self.update()

    def find_nearest_cabbage(self):
        goat = self.goat_herd[0]
        nearest_cabbage = min(self.cabbages, key=lambda c: math.sqrt((goat.x - c.x) ** 2 + (goat.y - c.y) ** 2))
        return nearest_cabbage

    def paintEvent(self, event):
        qp = QPainter(self)
        self.draw_field(qp)

    def draw_field(self, qp):
        for cabbage in self.cabbages:
            qp.setBrush(QColor(100, 255, 0))
            qp.drawEllipse(int(cabbage.x - cabbage.size // 2), int(cabbage.y - cabbage.size // 2), int(cabbage.size),
                           int(cabbage.size))

        for goat in self.goat_herd:
            if goat.is_eating:
                qp.setBrush(QColor(0, 0, 255))
                qp.drawPie(int(goat.x - goat.size // 2), int(goat.y - goat.size // 2),
                           int(goat.size), int(goat.size), 0, 180 * 16)
            else:
                qp.setBrush(QColor(0, 0, 255))
                qp.drawEllipse(int(goat.x - goat.size // 2), int(goat.y - goat.size // 2),
                               int(goat.size), int(goat.size))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            new_cabbage = Cabbage(random.randint(50, 350), random.randint(50, 350))
            self.cabbages.append(new_cabbage)
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    field = Field()
    sys.exit(app.exec())
