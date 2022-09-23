import time
from multiprocessing.connection import Client

import numpy

from Constants import GET_VECTORS_MESSAGE, SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY, LOG_FILE_PATH, VECTORS_PER_SECOND
from StatisticsLogger import ResultsLogger


class VectorProcessor:
    def __init__(self):
        self.client = VectorProcessor.get_client()
        self.results_logger = ResultsLogger(LOG_FILE_PATH)
        self.start_time = None
        self.received_vectors_count = 0

        self.acquisition_rates = []

    def start(self):
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
                now = time.time()

                d = time.time() - interval_start_time
                if d >= 0.1:
                    rate = interval_vectors_count / d
                    self.acquisition_rates.append(rate)
                    interval_start_time = time.time()
                    interval_vectors_count = 0

                    if len(self.acquisition_rates) % 10 == 0:
                        # calculate mean and std
                        mean = numpy.mean(self.acquisition_rates)
                        std = numpy.std(self.acquisition_rates)

                        # todo change this to results logger instead of print
                        print(f'Rate acquisition mean: {mean}, std: {std}')

                    # Check if a second has passed
                    packet_loss_interval_duration = time.time() - packet_loss_start_time
                    if packet_loss_interval_duration >= 1:
                        print(f'total counter: {self.received_vectors_count}')
                        print(f'Inside the condition. packet loss counter: {packet_loss_vectors_counter}')
                        packet_loss_vectors_counter -= VECTORS_PER_SECOND
                        packet_loss_start_time = time.time()

                        if packet_loss_vectors_counter < 0:
                            print('[WARNING] Seems like a packet was lost in transit')
                            time.sleep(2)
                            packet_loss_vectors_counter = 0

                # self.print_current_rate(now)

        finally:
            self.client.close()

    def print_current_rate(self, now):
        total_run_duration = now - self.start_time
        rate = self.received_vectors_count / total_run_duration
        print(f'[{int(now)}] Received {self.received_vectors_count} vectors in {total_run_duration:.2f} '
              f'seconds, which is a rate of {rate}')

    @staticmethod
    def get_client():
        address = (SERVER_HOST, SERVER_PORT)
        return Client(address, authkey=SERVER_AUTH_KEY)


if __name__ == '__main__':
    vector_processor = VectorProcessor()
    vector_processor.start()
