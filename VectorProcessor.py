import time

import numpy

from Constants import GET_VECTORS_MESSAGE, LOG_FILE_PATH, VECTORS_IN_MATRIX
from StatisticsLogger import ResultsLogger
from VectorGenerator import VectorGenerator

packet_loss_start_time = 0


class VectorProcessor:
    def __init__(self):
        self.client = VectorGenerator.get_client()
        self.stats_logger = ResultsLogger(LOG_FILE_PATH)
        self.start_time = None
        self.received_vectors_count = 0

        self.acquisition_rates = []

    def start(self):
        global packet_loss_start_time
        try:
            self.client.send(GET_VECTORS_MESSAGE)

            self.start_time = time.time()
            interval_start_time = self.start_time

            interval_vectors_count = 0
            matrix = []

            while True:
                now = time.time()
                matrix.append(self.client.recv())
                if self.check_for_packet_loss(now):
                    self.received_vectors_count += 1
                self.received_vectors_count += 1
                interval_vectors_count += 1

                d = time.time() - interval_start_time
                if d >= 0.1:
                    rate = interval_vectors_count / d
                    self.acquisition_rates.append(rate)
                    interval_start_time = time.time()
                    interval_vectors_count = 0

                    self.log_acquisition_rate_statistics()

                # For each matrix, calculate and write to the fs the mean and std
                if len(matrix) == VECTORS_IN_MATRIX:
                    mean_vector = numpy.mean(matrix, axis=0).tolist()
                    std = numpy.std(matrix, axis=0).tolist()
                    self.stats_logger.log_matrix_statistics(mean_vector, std)
                    matrix = []

                self.print_current_rate(now)
        finally:
            self.client.close()

    @staticmethod
    def check_for_packet_loss(now):
        ms_in_seconds = 1_000
        after_send = int(time.time() * ms_in_seconds)
        if after_send > int(now * ms_in_seconds) + 1:
            print('[WARNING] Seems like a packet was lost in transit')
            return True
        return False

    def log_acquisition_rate_statistics(self):
        # calculate mean and std for every 10 vectors received
        if len(self.acquisition_rates) % 10 == 0:
            acquisition_mean = numpy.mean(self.acquisition_rates)
            acquisition_std = numpy.std(self.acquisition_rates)

            self.stats_logger.log_acquisition_rate_statistics(self.acquisition_rates, acquisition_mean, acquisition_std)

    def print_current_rate(self, now):
        total_run_duration = now - self.start_time

        # Handle the launch of the program
        if total_run_duration == 0:
            return

        rate = self.received_vectors_count / total_run_duration
        print(f'[{now}] Received {self.received_vectors_count} vectors in {total_run_duration:.3f} '
              f'seconds, which is a rate of {rate} vectors/second')


if __name__ == '__main__':
    vector_processor = VectorProcessor()
    vector_processor.start()
