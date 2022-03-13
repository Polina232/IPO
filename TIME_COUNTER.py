from states import Timestamp

WORDS_IN_MESSAGE = 12
TIME_PER_WORD = 20
TIME_IF_BUSY = 250
TIME_FOR_MESSAGE = 50

class TimeCounter:
    def __init__(self):
        self.__timestamps__ = {
            Timestamp.WORD: WORDS_IN_MESSAGE * TIME_PER_WORD,
            Timestamp.COMMAND: TIME_PER_WORD,
            Timestamp.ANSWER: TIME_PER_WORD,
            Timestamp.BLOCK: TIME_PER_WORD,
            Timestamp.UNBLOCK: TIME_PER_WORD,
            Timestamp.WAIT_IF_BUSY: TIME_IF_BUSY * TIME_PER_WORD,
            Timestamp.WAIT_FOR_ANSWER: WORDS_IN_MESSAGE,
            Timestamp.WAIT_FOR_MESSAGE: TIME_FOR_MESSAGE * TIME_PER_WORD
        }
        self._total_wasted_time = 0

    def append_time(self, timestamp: Timestamp):
        self._total_wasted_time += self.__timestamps__[timestamp]

    def get_wasted_time(self):
        return self._total_wasted_time

