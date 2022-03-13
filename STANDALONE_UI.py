import tkinter as tk
import datetime as dt

from LCS import LCS
from states import DeviceState, LineState
from threading import Thread

state_to_color = {
    DeviceState.WORKING: 'green',
    DeviceState.DENIAL: 'red',
    DeviceState.BUSY: 'orange',
    DeviceState.FAILURE: 'yellow',
    DeviceState.BLOCKED: 'purple',
    DeviceState.GENERATOR: 'blue',
}
options_map = {
    'Раб': DeviceState.WORKING,
    'Отк': DeviceState.DENIAL,
    'Зан': DeviceState.BUSY,
    'Сбой': DeviceState.FAILURE,
    'Блок': DeviceState.BLOCKED,
    'Ген': DeviceState.GENERATOR,
    'Разблок': DeviceState.UNBLOCKING
}
state_to_name = {value: key for key, value in options_map.items()}
class TerminalDeviceView(tk.Frame):
    def __init__(self, root, device_index, devices_cb, is_up):
        super().__init__(root, width=300, height=100) #Функция super(), возвращает объект объект-посредник,
                    # который делегирует вызовы метода родительскому или родственному классу, указанного type типа
        self.index = device_index
        self.devices_cb = devices_cb

        self.device_state_view = tk.Frame(self, bg='#000000', width=10, height=10) #делаем маленькие окна
        self.device_state_view.grid(row=1, column=0) #в строку

        options = ['Раб', 'Отк', 'Зан', 'Сбой', 'Блок', 'Ген']

        self.device_state = tk.StringVar() #??помогает более эффективно управлять значением виджета, такого как a LabelилиEntry
        self.states_option_menu = tk.OptionMenu(self, self.device_state, *options) #выпадающее или всплывающее меню,
                                # которое отображает группу объектов при нажатии или событии клавиатуры
                                # и позволяет пользователю выбирать один вариант за раз.
        self.states_option_menu.grid(row=0, column=0)

        terminals = devices_cb()
        terminals[self.index].append_state_change_callback(self._recolor_on_state)
        terminals[self.index].change_state(DeviceState.WORKING)

        self._name_label = tk.Label(self, text=f'ОУ №{self.index + 1}')#позволяет выводить статический текст без возможности редактирования
        self._name_label.grid(row=2, column=0)
        self.process_state_change()
        self._is_up = is_up
        self.configure(highlightbackground="green", highlightcolor="green", highlightthickness=5)#конфигурируем окно

    def process_state_change(self):
        devices = self.devices_cb()

        value = self.device_state.get()

        if len(value) != 0:
            devices[self.index].change_state(options_map[value])#из TERMINAL_DEVICE
            self._recolor_on_state()

    def _recolor_on_state(self): # изменяем цвет состояния
        devices = self.devices_cb()
        state = devices[self.index].state
        self.device_state.set(state_to_name[state])
        self.device_state_view.configure(bg=state_to_color[state])

    def is_up(self): # рычаг выкл/вкл
        return self._is_up

    def on_message(self, is_active): # цвет в сообщении
        color = "#5FFFAF" if is_active else "white"
        self.configure(bg=color)
        self._name_label.configure(bg=color)


class ControllerView(tk.Canvas):
    def __init__(self, root): #рисуем переключатеть основной линии А и дополнительной В
        super().__init__(root, width=80, height=50)
        self._text_label = tk.Label(self, text='К-A')
        self._text_label.place(x=30, y=5)
        self._text_label = tk.Label(self, text='К-B')
        self._text_label.place(x=30, y=34)
        self.create_line(0, 30, 90, 30, fill="red", width=5)
        self.configure(highlightbackground="red", highlightcolor="red", highlightthickness=5)


class LCSRunThread(Thread): #запуск демонстрационной млдели ЛВС
    def __init__(self, task):
        Thread.__init__(self)
        self.task = task

    def run(self):
        try:
            self.task()
        except Exception as e:
            print(e)


ACTIVE_COLOR = "green"
GENERATION_COLOR = "blue"
INACTIVE_COLOR = "gray"

class DataLineView:
    def __init__(self, root: tk.Canvas, name, position_start, position_end):
        #tk.Canvas - создаются объекты-холсты, на которых можно "рисовать"
        self._root = root
        self._name_label = self._root.create_text(position_end[0] - 20, position_end[1], text=name)
        self._data_line_position = position_end

        self._lines = [self._root.create_line(position_start[0], position_start[1], position_end[0],
                                              position_end[1],
                                              width=5),
        self._root.create_line(position_end[0], position_end[1], position_end[0] + 1700,
                                              position_end[1], width=5)] #формируем линию

    def activate(self): #изменяем цвета линии при разных состояниях
        for line_index in self._lines:
            self._root.itemconfig(line_index, fill=ACTIVE_COLOR)

    def deactivate(self):
        for line_index in self._lines:
            self._root.itemconfig(line_index, fill=INACTIVE_COLOR)

    def generation(self):
        for line_index in self._lines:
            self._root.itemconfig(line_index, fill=GENERATION_COLOR)

    def connect_terminal(self, terminal: TerminalDeviceView): #линии для соединения оу
        is_up = terminal.is_up()
        x_position = terminal.winfo_x() + terminal.winfo_width() / 2 #находим координаты центра окна маленькогоокна статуса линии?
        y_position = terminal.winfo_y() if is_up else terminal.winfo_y() + terminal.winfo_height()

        self._lines.append(self._root.create_line(x_position, y_position, x_position, self._data_line_position[1],
                                                  width=5))
        #Первые два параметра это координаты x,y первой точки начало отрезка.
        # Вторые два параметры это координаты x,y второй точки конец отрезка.
        # width - толщина линии.
class LCSView(tk.Canvas):
    def __init__(self, root, logger_cb, height=250, width=1600):
        super().__init__(root, height=height, width=width)

        terminals_count = 18 #кол-во оконечных устройств
        #рисуем основные линию А и дополнит В
        self._top_data_line = DataLineView(self, "A", (50, 115), (50, 10))
        self._bot_data_line = DataLineView(self, "B", (50, 135), (50, 245))

        self._lcs = LCS(terminals_count=terminals_count, probabilities=[0, 0, 0, 0],
                        line_state_change_handler=self.on_line_state_changed, logger_cb=logger_cb,
                        on_message=self.on_message)
        self._terminal_views = []
        column = 1

        for i in range(int(terminals_count)):# каждое устройстро ресуем
            top_terminal = TerminalDeviceView(self, i, self._lcs.get_terminals, True)
            bot_terminal = TerminalDeviceView(self, i, self._lcs.get_terminals, False)
            top_terminal.place(x=110 + 80 * i, y=60) #расспологаем в окне
            bot_terminal.place(x=110 + 80 * i, y=130)

            self._terminal_views.append(top_terminal) #добавляем в список
            self._terminal_views.append(bot_terminal)

            self.update_idletasks() #функция используется если были внесены изменения в состояние приложения,
            # и вы хотите, чтобы эти изменения были отображены на экране немедленно

            self._top_data_line.connect_terminal(top_terminal) #соединяем линиямии
            self._bot_data_line.connect_terminal(bot_terminal)

            column += 1

        self._bot_data_line.deactivate() #устанавливаем актив или не актив
        self._top_data_line.activate()
        self._controller_view = ControllerView(self) #переключатеть
        self._controller_view.place(x=10, y=115)
        self.configure(bg="white")

    def get_terminal_views(self):
        return self._terminal_views

    def get_lcs_thread(self):
        return LCSRunThread(self._lcs.process)

    def on_line_state_changed(self, state): #меняем состояние линии
        if state == LineState.WORKING_LINE_B:
            self._bot_data_line.activate()
            self._top_data_line.deactivate()
        elif state == LineState.GENERATION:
            self._top_data_line.generation()
            self._bot_data_line.deactivate()
        else:
            self._top_data_line.activate()
            self._bot_data_line.deactivate()

    def on_message(self, index, is_active):
        line_state = self._lcs.get_last_state()
        terminal = 2 * index + 1 if line_state == LineState.WORKING_LINE_B else 2 * index
        self._terminal_views[terminal].on_message(is_active)


class Logger(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=900, height=500)
        self.canvas = tk.Canvas(self, width=1000, height=500, scrollregion=(0, 0, 4999, 4999), bg="white")

        self.text_frame = tk.Frame(self.canvas, bg="white", width=1000, height=500)
        self.scroll_bar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)#создаем ползунок
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y) #устанавливаем ползунок

        self.canvas.configure(yscrollcommand=self.scroll_bar.set)
        self.canvas.create_window(0, 0, window=self.text_frame, anchor='nw') #создаем само окно скроллбар
        self.canvas.pack(side=tk.LEFT)

        self._row = 1

    def log(self, log_message):
        text_label = tk.Label(self.text_frame, font="Courier", text=f"{dt.datetime.now()}", bg="white")#позволяет выводить статический текст без возможности редактирования
        text_label.grid(row=self._row, column=0)#делаем "сетку" (таблицу) первая отвечает за дату текущую
        text_label = tk.Label(self.text_frame, font="Courier", text=f"{log_message}", bg="white")
        text_label.grid(row=self._row, column=1)#вторая за сами логи

        self._row += 1


class StandaloneUI(tk.Frame): #создание самого окна с кнопками, ЛВС и окна с логами
    def __init__(self, root, change_frame_cb):
        super().__init__(root)
        self._change_frame_button = tk.Button(self, text='Перейти к статистической модели', command=change_frame_cb)
        self._change_frame_button.grid(column=0, row=0)

        self._logger_view = Logger(self)
        self._logger_view.grid(column=0, row=2)

        self._lcs_frame = LCSView(self, self._logger_view.log)
        self._lcs_frame.grid(column=0, row=1)

        self._state_select_button = tk.Button(self, text='Применить состояния ОУ',
                                              command=self._on_state_select_clicked)
        self._state_select_button.grid(row=3, column=0)
        self._start_button = tk.Button(self, text='Запустить', command=self._on_start_clicked)
        self._start_button.grid(row=4, column=0)
        self.configure(bg="white")

    def _on_start_clicked(self):#нажать на кнопку
        self._lcs_frame.get_lcs_thread().start()

    def _on_clear_clicked(self):
        self._lcs = LCS(4, [0, 0, 0, 0])

    def _on_state_select_clicked(self):
        for index in range(len(self._lcs_frame.get_terminal_views())):
            self._lcs_frame.get_terminal_views()[index].process_state_change()

