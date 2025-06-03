import sys, random, math
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QSpinBox, QDoubleSpinBox, QSlider, QDialog,
    QFormLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout
)


class Goat:
    def __init__(self, x, y, size=20, endurance=0.1, speed=5):
        self.x = x
        self.y = y
        self.size = size
        self.endurance = endurance  # Выносливость (уменьшение размера при голоде)
        self.speed = speed
        self.is_eating = False
        self.eat_progress = 0
        self.is_dead = False

    def move_towards(self, cabbage_x, cabbage_y):
        dx = cabbage_x - self.x
        dy = cabbage_y - self.y
        distance = math.hypot(dx, dy)
        if distance > 1:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

    def eat_cabbage(self, cabbage_fertility):
        self.is_eating = True
        self.size += cabbage_fertility

    def hunger(self):
        self.size -= self.endurance
        if self.size <= 5:
            self.is_dead = True

    def reset_eating(self):
        self.is_eating = False
        self.eat_progress = 0


class Cabbage:
    def __init__(self, x, y, size=15, fertility=0.2):
        self.x = x
        self.y = y
        self.size = size
        self.fertility = fertility  # Плодородность капусты
        self.is_eaten = False
        self.size_decreasing_timer = QTimer()
        self.size_decreasing_timer.timeout.connect(self.decrease_size)
        self.size_decreasing_timer.start(500)

    def decrease_size(self):
        if not self.is_eaten and self.size > 0:
            self.size -= 0.05
            if self.size <= 0:
                self.is_eaten = True


class AddCabbageDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить капусту")
        self.setGeometry(300, 300, 300, 150)

        self.size_input = QSpinBox(self)
        self.size_input.setRange(5, 100)
        self.size_input.setValue(15)

        self.fertility_input = QSlider(Qt.Orientation.Horizontal, self)
        self.fertility_input.setRange(0, 100)
        self.fertility_input.setValue(20)
        self.fertility_input.setTickInterval(1)
        self.fertility_input.setTickPosition(QSlider.TickPosition.TicksBelow)

        self.ok_button = QPushButton("Добавить капусту", self)
        self.cancel_button = QPushButton("Отмена", self)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout = QFormLayout()
        layout.addRow("Размер капусты:", self.size_input)
        layout.addRow("Плодородность капусты:", self.fertility_input)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def get_cabbage_size(self):
        return self.size_input.value()

    def get_cabbage_fertility(self):
        return self.fertility_input.value() / 100  # Конвертируем в коэффициент


class EditGoatDialog(QDialog):
    def __init__(self, goat):
        super().__init__()
        self.setWindowTitle("Редактировать параметры стада")
        self.setGeometry(300, 300, 300, 200)

        self.size_input = QSpinBox(self)
        self.size_input.setRange(5, 100)
        self.size_input.setValue(int(goat.size))

        self.endurance_input = QDoubleSpinBox(self)
        self.endurance_input.setRange(0.0, 1.0)
        self.endurance_input.setSingleStep(0.01)
        self.endurance_input.setValue(goat.endurance)

        self.speed_input = QSpinBox(self)
        self.speed_input.setRange(1, 20)
        self.speed_input.setValue(int(goat.speed))

        self.ok_button = QPushButton("Сохранить", self)
        self.cancel_button = QPushButton("Отмена", self)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout = QFormLayout()
        layout.addRow("Размер стада:", self.size_input)
        layout.addRow("Выносливость:", self.endurance_input)
        layout.addRow("Скорость:", self.speed_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)

        self.setLayout(layout)

    def get_size(self):
        return self.size_input.value()

    def get_endurance(self):
        return self.endurance_input.value()

    def get_speed(self):
        return self.speed_input.value()


class FieldArea(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_goat = None
            for goat in self.parent.goat_herd:
                distance = math.hypot(event.pos().x() - goat.x, event.pos().y() - goat.y)
                if distance <= goat.size / 2:
                    clicked_goat = goat
                    break
            if clicked_goat:
                edit_dialog = EditGoatDialog(clicked_goat)
                if edit_dialog.exec() == QDialog.DialogCode.Accepted:
                    clicked_goat.size = edit_dialog.get_size()
                    clicked_goat.endurance = edit_dialog.get_endurance()
                    clicked_goat.speed = edit_dialog.get_speed()
                    self.update()
            else:
                if self.parent.add_cabbage_dialog.exec() == QDialog.DialogCode.Accepted:
                    size = self.parent.add_cabbage_dialog.get_cabbage_size()
                    fertility = self.parent.add_cabbage_dialog.get_cabbage_fertility()
                    new_cabbage = Cabbage(event.pos().x(), event.pos().y(), size, fertility)
                    self.parent.cabbages.append(new_cabbage)
                    self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        self.parent.draw_field(qp)


class Field(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.goat_herd = []
        self.cabbages = [Cabbage(random.randint(50, 550), random.randint(50, 550), fertility=random.uniform(0.1, 0.5)) for _ in range(5)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_field)
        self.timer.start(50)

        self.add_cabbage_dialog = AddCabbageDialog()
        self.goat_moving = True

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Goats and Cabbages')

        main_layout = QHBoxLayout(self)

        self.field_area = FieldArea(self)
        self.field_area.setFixedSize(600, 600)
        main_layout.addWidget(self.field_area)

        self.controls_layout = QVBoxLayout()
        self.controls_layout.addSpacing(5)

        self.size_input = QSpinBox(self)
        self.size_input.setRange(1, 100)
        self.size_input.setValue(20)
        self.size_label = QLabel("Размер стада:", self)

        self.speed_input = QSlider(Qt.Orientation.Horizontal, self)
        self.speed_input.setRange(1, 10)
        self.speed_input.setValue(5)
        self.speed_input.setTickInterval(1)
        self.speed_input.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_label = QLabel("Скорость стада:", self)

        self.endurance_input = QSlider(Qt.Orientation.Horizontal, self)
        self.endurance_input.setRange(1, 10)
        self.endurance_input.setValue(1)
        self.endurance_input.setTickInterval(1)
        self.endurance_input.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.endurance_label = QLabel("Выносливость стада:", self)

        self.add_goat_herd_button = QPushButton("Добавить новое стадо", self)
        self.add_goat_herd_button.clicked.connect(self.add_new_goat_herd)

        self.controls_layout.addWidget(self.size_label)
        self.controls_layout.addWidget(self.size_input)

        self.controls_layout.addWidget(self.speed_label)
        self.controls_layout.addWidget(self.speed_input)

        self.controls_layout.addWidget(self.endurance_label)
        self.controls_layout.addWidget(self.endurance_input)

        self.controls_layout.addWidget(self.add_goat_herd_button)

        self.stop_start_button = QPushButton("Стоп движение", self)
        self.stop_start_button.clicked.connect(self.toggle_goat_movement)
        self.controls_layout.addWidget(self.stop_start_button)

        self.controls_layout.addStretch()

        self.controls_panel = QWidget(self)
        self.controls_panel.setLayout(self.controls_layout)
        self.controls_panel.setFixedWidth(200)
        main_layout.addWidget(self.controls_panel)

        self.setLayout(main_layout)

        self.show()

    def add_new_goat_herd(self):
        herd_size = self.size_input.value()
        speed = self.speed_input.value()
        endurance = self.endurance_input.value() / 100
        new_goat = Goat(random.randint(50, 550), random.randint(50, 550), size=herd_size, endurance=endurance, speed=speed)
        self.goat_herd.append(new_goat)
        self.update()

    def toggle_goat_movement(self):
        self.goat_moving = not self.goat_moving

        if self.goat_moving:
            self.stop_start_button.setText("Стоп движение")
            self.timer.start(50)
        else:
            self.stop_start_button.setText("Старт движение")
            self.timer.stop()

    def find_nearest_cabbage(self, goat):
        min_distance = float('inf')
        nearest_cabbage = None
        for cabbage in self.cabbages:
            if not cabbage.is_eaten:
                distance = math.hypot(goat.x - cabbage.x, goat.y - cabbage.y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_cabbage = cabbage
        return nearest_cabbage

    def update_field(self):
        if not self.goat_moving:
            return

        self.goat_herd = [goat for goat in self.goat_herd if not goat.is_dead]

        for goat in self.goat_herd:
            nearest_cabbage = self.find_nearest_cabbage(goat)
            if nearest_cabbage:
                goat.move_towards(nearest_cabbage.x, nearest_cabbage.y)
                distance = math.hypot(goat.x - nearest_cabbage.x, goat.y - nearest_cabbage.y)
                if distance < 10:
                    goat.eat_cabbage(nearest_cabbage.fertility)
                    nearest_cabbage.size -= 1
                    if nearest_cabbage.size <= 0:
                        nearest_cabbage.is_eaten = True
                        self.cabbages.remove(nearest_cabbage)
            else:
                goat.hunger()

            if goat.is_eating and (nearest_cabbage is None or nearest_cabbage.size <= 0):
                goat.is_eating = False

        self.field_area.update()

    def draw_field(self, qp):
        for cabbage in self.cabbages:
            if not cabbage.is_eaten:
                qp.setBrush(QColor(100, 255, 0))
                qp.drawEllipse(int(cabbage.x - cabbage.size / 2), int(cabbage.y - cabbage.size / 2),
                               int(cabbage.size), int(cabbage.size))

        for goat in self.goat_herd:
            if goat.is_eating:
                qp.setBrush(QColor(0, 0, 255))
                qp.drawPie(int(goat.x - goat.size / 2), int(goat.y - goat.size / 2),
                           int(goat.size), int(goat.size), 0, 180 * 16)
            else:
                qp.setBrush(QColor(0, 0, 255))
                qp.drawEllipse(int(goat.x - goat.size / 2), int(goat.y - goat.size / 2),
                               int(goat.size), int(goat.size))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    field = Field()
    sys.exit(app.exec())
