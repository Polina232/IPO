import tkinter as tk  #библиотека графического интерфейса с оконным интерфейсом
from statistics_ui import StatisticsUI #ввод пользователем входных данных
from STANDALONE_UI import StandaloneUI #отображение демонстрационной модели

COLOR = 'grey'
BUTTON_HEIGHT = 15
BUTTON_WIDTH = 15


class Window:
    # конструктор
    def __init__(self, window_height=900, window_width=600, window_position_height=600, window_position_width=400):
        self._window_height = window_height
        self._window_width = window_width
        self._window_position_height = window_position_height
        self._window_position_width = window_position_width
        self._buttons = []
        self._root = tk.Tk()  # создает базовое окно
        self._root.attributes("-fullscreen",
                              True)  # полноэкранный режим (-fullscreen указывает, находится ли окно в полноэкранном режиме или нет)
        self._root.bind("<Escape>",
                        self._on_escape_clicked)  # привязывает событие к какому-либо действию (событие Escape)

        self.frames = {0: StatisticsUI(root=self._root, change_frame_cb=self._on_change_frame_clicked),  # ввод данных
                       1: StandaloneUI(root=self._root,
                                       change_frame_cb=self._on_change_frame_clicked)}  # демонстрация модели
        self.active_frame = 1

        # запуск интерфейса
        def start_gui(self):
            self._root.title("LVS")  # название окна
            self._root.geometry(
                f'{self._window_height}x{self._window_width}+{self._window_position_height}+{self._window_position_width}')  # расширение
            self._on_change_frame_clicked()
            self._root.configure(bg="white")
            self._root.mainloop()  # запустить цикл событий (блокирует выполнение кода пока окно открыто) (бесконечный цикл окна приложения, чтобы было видеть неподвижное окно)

        # выход из полноэкранного режима
        def _on_escape_clicked(self, event=None):
            self._root.attributes("-fullscreen", False)

        # переключение между фреймами (между вводом данных и демонстрацией)
        def _on_change_frame_clicked(self):
            self.frames[self.active_frame].grid_forget()  # grid_forget() делает виджеты невидимыми
            self.active_frame = 0 if self.active_frame == 1 else 1
            frame = self.frames[self.active_frame]
            frame.grid(row=0, column=0)  # задает сетку (нулевая строка, нулевая ячейка)