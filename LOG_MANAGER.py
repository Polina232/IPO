class LogManager:
    # конструктор
    def __init__(self):
        self._waiting_messages = {}
        self._listeners = []

    def append_listener(self, listener):
        self._listeners.append(listener)

    # метод, принимающий на вход номер устройства и сообщение, полученное устройством.
    def on_message(self, device_id, message):
        for listener in self._listeners:  # self._listeners
            self._waiting_messages[listener].append(message)

    # метод, возвращающий список всех  сообщений, которые получатель логов ещё не успел получить
    def get_ready_messages(self, client_id):
        return self._waiting_messages[client_id].pop()