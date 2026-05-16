import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


# ============= ДИАЛОГ СОЗДАНИЯ/РЕДАКТИРОВАНИЯ СОБЫТИЯ (ТОЛЬКО ФОРМА) =============
class EventDialog(QDialog):
    """Диалоговое окно для создания/редактирования события"""

    def __init__(self, parent, event=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Создание события" if not event else "Редактирование события"
        )
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Название события
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название события")
        layout.addRow("📝 Название:", self.name_edit)

        # Время начала
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        layout.addRow("⏰ Время начала:", self.time_edit)

        # Длительность
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 480)
        self.duration_spin.setSingleStep(15)
        self.duration_spin.setSuffix(" минут")
        layout.addRow("⌛ Длительность:", self.duration_spin)

        # Регулярность
        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems(["❌ Нет", "🔄 Ежедневно", "📅 Еженедельно"])
        layout.addRow("🔄 Регулярность:", self.recurrence_combo)

        # Привязанная папка
        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Путь к папке")
        self.folder_edit.setReadOnly(True)
        btn_folder = QPushButton("📁 Выбрать")
        btn_folder.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(btn_folder)
        layout.addRow("📂 Папка:", folder_layout)

        # Разделитель
        layout.addRow(QLabel("=" * 50))
        layout.addRow(QLabel("👥 Посещаемость (отметьте присутствующих):"))

        # Список пользователей с чекбоксами (демо-данные для отображения)
        self.user_checkboxes = []
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # ВРЕМЕННЫЕ ДЕМО-ДАННЫЕ ДЛЯ ОТОБРАЖЕНИЯ ФОРМЫ
        demo_users = [
            {"id": 1, "name": "Иван Петров", "label": "Студент"},
            {"id": 2, "name": "Мария Сидорова", "label": "Студентка"},
            {"id": 3, "name": "Алексей Иванов", "label": "Преподаватель"},
        ]

        for user in demo_users:
            cb = QCheckBox(f"{user['name']} — {user['label']}")
            scroll_layout.addWidget(cb)
            self.user_checkboxes.append(cb)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setMaximumHeight(200)
        layout.addRow(scroll_area)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def select_folder(self):
        """Выбор папки"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для события")
        if folder:
            self.folder_edit.setText(folder)

    def get_event_data(self):
        """ВОЗВРАЩАЕТ ДАННЫЕ ИЗ ФОРМЫ ДЛЯ ПЕРЕДАЧИ В БЭКЕНД
        Здесь backend должен забрать эти данные и сохранить
        """
        return {
            "name": self.name_edit.text(),
            "start_time": self.time_edit.time().toString(),
            "duration": self.duration_spin.value(),
            "recurrence": self.recurrence_combo.currentText(),
            "folder_path": self.folder_edit.text(),
            "attendance": [cb.isChecked() for cb in self.user_checkboxes],
        }


# ============= ОКНО РЕЖИМА ПОСЕЩАЕМОСТИ (ТОЛЬКО КАМЕРА И СПИСОК) =============
class AttendanceWindow(QMainWindow):
    """Окно с камерой для сканирования QR/карт"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("🎥 Режим посещаемости - Сканер")
        self.setGeometry(200, 200, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Информация о событии (демо-данные)
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #2c3e50; border-radius: 10px; padding: 10px;"
        )
        info_layout = QVBoxLayout(info_frame)

        info_layout.addWidget(QLabel("📌 Событие: Лекция по Python"))
        info_layout.addWidget(QLabel("⏰ Время: 14:00 (90 мин)"))
        info_layout.addWidget(QLabel("📂 Папка: /путь/к/папке"))

        layout.addWidget(info_frame)

        # Виджет камеры (заглушка, т.к. камера может не работать)
        layout.addWidget(QLabel("🎥 Наведите QR-код или карту на камеру:"))

        # МЕСТО ДЛЯ ВИДЖЕТА КАМЕРЫ
        # Здесь backend должен подставить реальный виджет камеры
        camera_placeholder = QLabel("📷 [Здесь будет окно камеры]")
        camera_placeholder.setAlignment(Qt.AlignCenter)
        camera_placeholder.setStyleSheet(
            "background-color: #1a1a1a; padding: 50px; border-radius: 10px;"
        )
        camera_placeholder.setMinimumHeight(300)
        layout.addWidget(camera_placeholder)

        # Результат сканирования
        self.result_label = QLabel("⏳ Ожидание сканирования...")
        self.result_label.setStyleSheet(
            "font-size: 14px; padding: 10px; background-color: #34495e; border-radius: 5px;"
        )
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        # Инструкция
        test_label = QLabel(
            "💡 Подсказка: для отметки пользователя дважды кликните по нему в списке"
        )
        test_label.setStyleSheet("color: #f39c12; font-size: 12px;")
        layout.addWidget(test_label)

        # Список пользователей для ручной отметки
        layout.addWidget(QLabel("👥 Ручная отметка (двойной клик для отметки):"))

        self.users_list = QListWidget()
        # ДЕМО-ДАННЫЕ ДЛЯ ОТОБРАЖЕНИЯ
        demo_users = [
            "Иван Петров — Студент",
            "Мария Сидорова — Студентка",
            "Алексей Иванов — Преподаватель",
        ]
        for user in demo_users:
            self.users_list.addItem(user)
        self.users_list.itemDoubleClicked.connect(self.manual_mark)
        self.users_list.setMaximumHeight(150)
        layout.addWidget(self.users_list)

        # Кнопка закрытия
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 8px;"
        )
        layout.addWidget(btn_close)

    def manual_mark(self, item):
        """Ручная отметка (двойной клик) — ПУСТАЯ ЗАГЛУШКА"""
        user_name = item.text()
        self.result_label.setText(
            f"✅ Отмечен: {user_name}\n(здесь backend отметит посещаемость)"
        )
        self.result_label.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px;"
        )

        # Визуально отмечаем в списке
        item.setBackground(QBrush(QColor(39, 174, 96, 100)))
        item.setText(f"✓ {item.text()}")


# ============= ГЛАВНОЕ ОКНО (ТОЛЬКО ИНТЕРФЕЙС) =============
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📅 Календарь событий")
        self.setGeometry(100, 100, 1300, 800)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ========== ЛЕВАЯ ПАНЕЛЬ: КАЛЕНДАРЬ И СОБЫТИЯ ==========
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        # Календарь
        left_layout.addWidget(QLabel("📅 КАЛЕНДАРЬ"))
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        left_layout.addWidget(self.calendar)

        # События на выбранный день
        left_layout.addWidget(QLabel("📋 СОБЫТИЯ НА ВЫБРАННЫЙ ДЕНЬ"))
        self.events_list = QListWidget()
        self.events_list.itemClicked.connect(self.on_event_selected)
        self.events_list.itemDoubleClicked.connect(self.edit_event)
        left_layout.addWidget(self.events_list)

        # Кнопки управления событиями
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)

        self.btn_create = QPushButton("➕ Создать событие")
        self.btn_create.clicked.connect(self.create_event)
        self.btn_create.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px;"
        )
        btn_layout.addWidget(self.btn_create)

        self.btn_delete_event = QPushButton("🗑️ Удалить событие")
        self.btn_delete_event.clicked.connect(self.delete_event)
        self.btn_delete_event.setEnabled(False)
        self.btn_delete_event.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 8px;"
        )
        btn_layout.addWidget(self.btn_delete_event)

        left_layout.addWidget(btn_frame)

        # Кнопка режима посещаемости
        self.btn_attendance = QPushButton("🎥 РЕЖИМ ПОСЕЩАЕМОСТИ")
        self.btn_attendance.clicked.connect(self.open_attendance_mode)
        self.btn_attendance.setEnabled(False)
        self.btn_attendance.setStyleSheet(
            "background-color: #2ecc71; color: white; padding: 12px; font-size: 14px; font-weight: bold;"
        )
        left_layout.addWidget(self.btn_attendance)

        # ========== ПРАВАЯ ПАНЕЛЬ: ПОЛЬЗОВАТЕЛИ ==========
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        right_layout.addWidget(QLabel("👥 ПОЛЬЗОВАТЕЛИ"))

        # Список пользователей
        self.users_list = QListWidget()
        self.users_list.itemClicked.connect(self.on_user_selected)
        right_layout.addWidget(self.users_list)

        # Панель редактирования пользователя
        edit_group = QGroupBox("✏️ Редактирование пользователя")
        edit_layout = QFormLayout(edit_group)

        self.user_name_label = QLabel()
        edit_layout.addRow("Имя:", self.user_name_label)

        self.user_label_edit = QLineEdit()
        self.user_label_edit.setPlaceholderText("Введите новый label")
        edit_layout.addRow(
            "🏷️ Label (только это поле можно редактировать):", self.user_label_edit
        )

        btn_save_label = QPushButton("💾 Сохранить изменения")
        btn_save_label.clicked.connect(self.save_user_label)
        btn_save_label.setStyleSheet("background-color: #3498db; color: white;")
        edit_layout.addRow(btn_save_label)

        edit_layout.addRow(QLabel("---" * 15))
        edit_layout.addRow(QLabel("🔐 Привязка идентификаторов:"))

        btn_qr = QPushButton("📱 Привязать QR-код")
        btn_qr.clicked.connect(self.bind_qr)
        btn_qr.setStyleSheet("background-color: #9b59b6; color: white;")
        edit_layout.addRow(btn_qr)

        btn_card = QPushButton("💳 Привязать карту")
        btn_card.clicked.connect(self.bind_card)
        btn_card.setStyleSheet("background-color: #e67e22; color: white;")
        edit_layout.addRow(btn_card)

        right_layout.addWidget(edit_group)

        # Статус привязок
        self.bind_status = QLabel(
            "Информация о привязках будет здесь после загрузки данных из бэкенда"
        )
        self.bind_status.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        right_layout.addWidget(self.bind_status)

        # Добавляем панели
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)

        # Заполняем демо-данными для отображения
        self.load_demo_data()

    def load_demo_data(self):
        """ЗАГРУЗКА ДЕМО-ДАННЫХ ДЛЯ ОТОБРАЖЕНИЯ ИНТЕРФЕЙСА"""
        # Демо-пользователи
        demo_users = [
            {
                "id": 1,
                "name": "Иван Петров",
                "label": "Студент группы А-21",
                "qr": "✅",
                "card": "❌",
            },
            {
                "id": 2,
                "name": "Мария Сидорова",
                "label": "Студентка группы Б-22",
                "qr": "❌",
                "card": "✅",
            },
            {
                "id": 3,
                "name": "Алексей Иванов",
                "label": "Преподаватель",
                "qr": "❌",
                "card": "❌",
            },
        ]

        for user in demo_users:
            item = QListWidgetItem(f"{user['name']}\n   └ {user['label']}")
            item.setData(Qt.UserRole, user["id"])
            self.users_list.addItem(item)

        # Демо-события на сегодня
        today = QDate.currentDate().toString("yyyy-MM-dd")
        demo_events = [
            {
                "name": "Лекция по Python",
                "time": "14:00",
                "duration": "90",
                "recurrence": "Еженедельно",
            },
            {
                "name": "Семинар по Qt",
                "time": "16:00",
                "duration": "60",
                "recurrence": "Нет",
            },
        ]

        for event in demo_events:
            item = QListWidgetItem(
                f"📌 {event['name']}\n   ⏰ {event['time']} ({event['duration']} мин)\n   🔄 {event['recurrence']}"
            )
            self.events_list.addItem(item)

    # ========== ВСЕ МЕТОДЫ НИЖЕ — ПУСТЫЕ ЗАГЛУШКИ ДЛЯ БЭКЕНДА ==========

    def on_date_selected(self, date):
        """Выбор даты в календаре — ЗДЕСЬ БЭКЕНД ДОЛЖЕН ЗАГРУЗИТЬ СОБЫТИЯ НА ЭТУ ДАТУ"""
        date_str = date.toString("yyyy-MM-dd")
        print(f"[FRONTEND] Выбрана дата: {date_str}")  # Заглушка
        # Бэкенд должен обновить self.events_list данными на эту дату
        self.btn_attendance.setEnabled(False)

    def on_event_selected(self, item):
        """Выбор события — ЗДЕСЬ БЭКЕНД ДОЛЖЕН СОХРАНИТЬ ВЫБРАННОЕ СОБЫТИЕ"""
        print(f"[FRONTEND] Выбрано событие: {item.text()}")
        self.btn_delete_event.setEnabled(True)
        self.btn_attendance.setEnabled(True)

    def create_event(self):
        """Создание события — ОТКРЫВАЕТ ФОРМУ, ДАННЫЕ ПЕРЕДАЁТ В БЭКЕНД"""
        dialog = EventDialog(self)
        if dialog.exec():
            event_data = dialog.get_event_data()
            print("[FRONTEND] Данные нового события:", event_data)  # Заглушка
            # ЗДЕСЬ БЭКЕНД ДОЛЖЕН СОХРАНИТЬ СОБЫТИЕ
            # И ОБНОВИТЬ СПИСОК СОБЫТИЙ

    def edit_event(self, item):
        """Редактирование события — ОТКРЫВАЕТ ФОРМУ С ДАННЫМИ, ОБНОВЛЕНИЕ ЧЕРЕЗ БЭКЕНД"""
        dialog = EventDialog(self, event=True)
        if dialog.exec():
            event_data = dialog.get_event_data()
            print("[FRONTEND] Обновлённые данные события:", event_data)  # Заглушка
            # ЗДЕСЬ БЭКЕНД ДОЛЖЕН ОБНОВИТЬ СОБЫТИЕ

    def delete_event(self):
        """Удаление события — ЗАПРОС ПОДТВЕРЖДЕНИЯ, ВЫЗОВ БЭКЕНДА ДЛЯ УДАЛЕНИЯ"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить выбранное событие?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            print("[FRONTEND] Удаление события")  # Заглушка
            # ЗДЕСЬ БЭКЕНД ДОЛЖЕН УДАЛИТЬ СОБЫТИЕ
            self.btn_delete_event.setEnabled(False)
            self.btn_attendance.setEnabled(False)

    def open_attendance_mode(self):
        """Режим посещаемости — ОТКРЫВАЕТ ОКНО С КАМЕРОЙ"""
        print("[FRONTEND] Открыт режим посещаемости")
        attendance_window = AttendanceWindow(self)
        attendance_window.show()

    def on_user_selected(self, item):
        """Выбор пользователя — ЗДЕСЬ БЭКЕНД ДОЛЖЕН ЗАГРУЗИТЬ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ"""
        user_id = item.data(Qt.UserRole)
        print(f"[FRONTEND] Выбран пользователь ID: {user_id}")
        # Демо-заполнение для отображения интерфейса
        self.user_name_label.setText(item.text().split("\n")[0])
        self.user_label_edit.setText(
            item.text().split("└")[1].strip() if "└" in item.text() else ""
        )
        self.bind_status.setText(
            "Информация из бэкенда появится здесь при подключении данных"
        )

    def save_user_label(self):
        """Сохранение label — ЗДЕСЬ БЭКЕНД ДОЛЖЕН ОБНОВИТЬ LABEL ПОЛЬЗОВАТЕЛЯ"""
        new_label = self.user_label_edit.text()
        print(f"[FRONTEND] Сохранение label: {new_label}")  # Заглушка
        # ЗДЕСЬ БЭКЕНД ДОЛЖЕН ОБНОВИТЬ ПОЛЕ LABEL У ПОЛЬЗОВАТЕЛЯ
        QMessageBox.information(
            self,
            "Успех",
            f"Label изменён на '{new_label}'\n(в бэкенде сохранится автоматически)",
        )

    def bind_qr(self):
        """Привязка QR — ОТКРЫВАЕТ ОКНО С КАМЕРОЙ, ДАННЫЕ В БЭКЕНД"""
        print("[FRONTEND] Привязка QR-кода")
        # ЗДЕСЬ БЭКЕНД ДОЛЖЕН ОТКРЫТЬ КАМЕРУ И ПОЛУЧИТЬ QR
        QMessageBox.information(
            self,
            "Привязка QR",
            "Открывается камера для сканирования QR-кода\n(здесь бэкенд обработает сканирование и сохранит QR)",
        )

    def bind_card(self):
        """Привязка карты — ПОКАЗЫВАЕТ УВЕДОМЛЕНИЕ, ДАННЫЕ В БЭКЕНД"""
        print("[FRONTEND] Привязка карты")
        # ЗДЕСЬ БЭКЕНД ДОЛЖЕН ПОКАЗАТЬ УВЕДОМЛЕНИЕ И ПОЛУЧИТЬ ID КАРТЫ
        QMessageBox.information(
            self,
            "Привязка карты",
            "Приложите карту к считывателю\n(здесь бэкенд прочитает ID карты и сохранит)",
        )


# ============= ЗАПУСК =============
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Стилизация интерфейса
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            background-color: #3c3c3c;
            color: #ffffff;
            font-family: 'Segoe UI', Arial;
        }
        QPushButton {
            background-color: #4a4a4a;
            border: none;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QListWidget, QCalendarWidget {
            background-color: #2b2b2b;
            border: 1px solid #555;
            border-radius: 5px;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QLineEdit, QTimeEdit, QSpinBox, QComboBox {
            background-color: #2b2b2b;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 5px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

