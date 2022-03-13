import time as t
from collections import Counter
from TERMINAL_DEVICE import TerminalDevice
from CONTROL_DEVICE import ControlDevice
from states import *

default_sleep_time_ms = 100

class LCS:
    def __init__(self, terminals_count: int, probabilities, system_type=LCSType.Standalone,
                 sleep_time=default_sleep_time_ms, line_state_change_handler=None, logger_cb=None,
                 on_message=None):
      self.type = system_type
      self.sleep_time_ms = sleep_time
      self.logger_cb = logger_cb
      self.controller = ControlDevice(self.get_terminals, self.line_state_change, self.type, self.sleep_time_ms)
      self.terminals = [TerminalDevice(system_type, index, probabilities, self.get_line_state, self.line_state_change,self.get_terminals, logger_cb, on_message)for index in range(terminals_count)]
      self.line_state = LineState.WORKING_LINE_A
      self.last_received_state = LineState.WORKING_LINE_A
      self.line_state_change_handler = line_state_change_handler

    #класс отвечает за контроль объектов и взаимодействие данных объектов между собой
    def process(self):
        broken_states = None
        if self.type == LCSType.Statistics:
            broken_states = Counter(filter(lambda state: DeviceState.BUSY.value <= state.value <= DeviceState.GENERATOR.value,map(lambda terminal: terminal.process(), self.terminals)))
        else:
            t.sleep(self.sleep_time_ms / 1000)
            if self.logger_cb:
              self.logger_cb('ЛВС - Запуск')

        while self.line_state == LineState.GENERATION:
          self.controller.process_generator_device()

        for terminal in self.terminals:
          self.controller.process_client_device(terminal)

        if self.type == LCSType.Standalone:
            self.logger_cb('ЛВС - Завершение')

        return broken_states

    def get_terminals(self):
        return self.terminals

    def get_line_state(self):
        return self.line_state

    def get_last_state(self):
        return self.last_received_state

    def line_state_change(self, new_state):
        if self.line_state_change_handler:
          self.line_state_change_handler(new_state)

          self.last_received_state = new_state

    def to_string(self, state):
          if state == LineState.GENERATION:
              return 'ГЕНЕРАЦИЯ'
          elif state == LineState.WORKING_LINE_A:
              return 'ЛИНИЯ А'
          else:
              return 'ЛИНИЯ B'

          if self.type == LCSType.Standalone:
              self.logger_cb(f"ЛПИ - {to_string(new_state)}")

          if any(map(lambda terminal: terminal.state == DeviceState.GENERATOR, self.terminals)):
              self.line_state = LineState.GENERATION
          else:
              self.line_state = new_state
