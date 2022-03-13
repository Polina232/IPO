import csv
from collections import Counter
from threading import Thread, Lock
from typing import List
#import lcs
#from states import LCSType, DeviceState
from STATISTIC_MODEL import Statistics, statistic_model, get_value_index, LCSRunThread
class StatisticRunner:
    def __init__(self, sessions_count, group_count, total_messages_count, terminals_count, probabilities,
                 task_bar_update_cb):
        self._statistics_per_run = 10
        assert sessions_count % self._statistics_per_run == 0, \
            f"Sessions count should be divisible by {self._statistics_per_run}"
        self._sessions_count = sessions_count
        self._group_count = group_count
        self._total_messages_count = total_messages_count
        self._terminals_count = terminals_count
        self._probabilities = probabilities
        self._task_bar_update_cb = task_bar_update_cb
        self._processed_count = 0
        self._run_index = 0
        self._mutex = Lock()

        self._results: List[Statistics] = []

    def make_statistic(self):
        self._mutex.acquire()
        index = self._run_index
        self._run_index += 1
        print(f"Running {index}")
        self._mutex.release()

        statistic = statistic_model(self._group_count,
                                    self._total_messages_count,
                                    self._terminals_count,
                                    self._probabilities.copy())[-1]
        statistic.run_index = index
        print(f"Finished {index}")

        self._mutex.acquire()
        self._task_bar_update_cb(1)
        self._processed_count += 1
        self._mutex.release()

        return statistic

    def make_single_run(self):
        result = [self.make_statistic() for _ in range(self._statistics_per_run)]
        self._mutex.acquire()
        self._results += result
        self._mutex.release()

    def run(self):
        for _ in range(int(self._sessions_count / self._statistics_per_run)):
            LCSRunThread(self.make_single_run).start()

    def is_ready(self):
        return self._processed_count == self._sessions_count

    def results(self):
        if not self.is_ready():
            return None

        self._results.sort(key=lambda stat: stat.run_index)
        total_statistic = Statistics()
        total_statistic.run_index = 50
        total_statistic.failures_count = sum(stat.failures_count for stat in self._results)
        total_statistic.busy_count = sum(stat.busy_count for stat in self._results)
        total_statistic.denials_count = sum(stat.denials_count for stat in self._results)
        total_statistic.generators_count = sum(1 for stat in self._results if stat.generators_count != 0)
        total_statistic.math_expectation = sum(stat.math_expectation for stat in self._results) / self._sessions_count
        total_statistic.standard_deviation = sum(
            stat.standard_deviation for stat in self._results) / self._sessions_count

        self._results.append(total_statistic)

        return self._results


def write_single_statistic_to_csv(output_filename, statistics):
    field_names = ['Тысяча сообщений', 'Отказов', 'Сбоев', '"АБонент занят"',
                   'Наличие генератора', 'Затраченное время, мс', 'МО', 'СКО']

    generator_index = get_value_index(statistics, 'generators_count')
    # If generator occured we should mark all runs as with generator
    if len(generator_index) != 0:
        def modify(stat):
            stat.generators_count = generator_index[0]
            return stat

        statistics = list(map(modify, statistics))

    with open(output_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(field_names)
        for statistic in statistics:
            writer.writerow(statistic.as_list())

        csv_file.close()


def write_sessions_statistic_to_csv(output_filename, statistics):
    field_names = ['Номер сеанса', 'Число сбоев', 'Число "абонент занят"', 'Число отказов и m для каждого из них',
                   'Число генераций и Nг для каждого из них', 'Среднее время передачи сообщения', 'СКО']

    with open(output_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(field_names)
        for index, statistic in enumerate(statistics):
            denials_stats = str(statistic.denials_count) + ": " + ",".join(map(str, statistic.denials_indices))

            # Index 50 is the total statistic it shouldn't be compressed
            if statistic.generators_count != 0 and index != 50:
                statistic.generators_count = 1
                statistic.generators_indices = statistic.generators_indices[:1]

            generator_stats = str(statistic.generators_count) + ": " + ",".join(map(str, statistic.generators_indices))

            row = [str(statistic.run_index),
                   str(statistic.failures_count),
                   str(statistic.busy_count),
                   denials_stats,
                   generator_stats,
                   str(statistic.math_expectation),
                   str(statistic.standard_deviation)]
            writer.writerow(row)

        csv_file.close()
