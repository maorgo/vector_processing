import time

import numpy

from Constants import GET_VECTORS_MESSAGE, LOG_FILE_PATH, VECTORS_PER_SECOND
from StatisticsLogger import ResultsLogger
from src.VectorGenerator import VectorGenerator

packet_loss_start_time = 0


class VectorProcessor:
    def __init__(self):
        self.client = VectorGenerator.get_client()
        self.results_logger = ResultsLogger(LOG_FILE_PATH)
        self.start_time = None
        self.received_vectors_count = 0

        self.acquisition_rates = []

    def start(self):
        global packet_loss_start_time
        try:
            self.client.send(GET_VECTORS_MESSAGE)

            self.start_time = time.time()
            interval_start_time = self.start_time
            packet_loss_start_time = self.start_time

            interval_vectors_count = 0
            packet_loss_vectors_counter = 0

            while True:
                vector = self.client.recv()
                self.received_vectors_count += 1
                interval_vectors_count += 1
                packet_loss_vectors_counter += 1

                d = time.time() - interval_start_time
                if d >= 0.1:
                    rate = interval_vectors_count / d
                    self.acquisition_rates.append(rate)
                    interval_start_time = time.time()
                    interval_vectors_count = 0

                    self.log_acquisition_rate_statistics()

                    packet_loss_vectors_counter = self.check_for_packet_loss(packet_loss_vectors_counter)

                # self.print_current_rate(now)

        finally:
            self.client.close()

    def check_for_packet_loss(self, packet_loss_vectors_counter):
        global packet_loss_start_time
        packet_loss_interval_duration = time.time() - packet_loss_start_time

        # Check if a second has passed
        if packet_loss_interval_duration >= 1:
            print(f'total counter: {self.received_vectors_count}')
            print(f'Inside the condition. packet loss counter: {packet_loss_vectors_counter}')
            packet_loss_vectors_counter -= VECTORS_PER_SECOND
            packet_loss_start_time = time.time()

            if packet_loss_vectors_counter < 0:
                print('[WARNING] Seems like a packet was lost in transit')
                time.sleep(2)
                packet_loss_vectors_counter = 0
        return packet_loss_vectors_counter

    def log_acquisition_rate_statistics(self):
        if len(self.acquisition_rates) % 10 == 0:
            # calculate mean and std for every 10
            acquisition_mean = numpy.mean(self.acquisition_rates)
            acquisition_std = numpy.std(self.acquisition_rates)

            self.results_logger.log_acquisition_rate_statistics(
                self.acquisition_rates, acquisition_mean, acquisition_std
            )

    def print_current_rate(self, now):
        total_run_duration = now - self.start_time
        rate = self.received_vectors_count / total_run_duration
        print(f'[{int(now)}] Received {self.received_vectors_count} vectors in {total_run_duration:.2f} '
              f'seconds, which is a rate of {rate}')


if __name__ == '__main__':
    vector_processor = VectorProcessor()
    vector_processor.start()
