import time
from argparse import ArgumentParser
from multiprocessing.connection import Listener

import numpy as numpy

from Constants import SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY, VECTORS_PER_SECOND


class VectorGenerator:
    def __init__(self):
        self.sent_vectors_count = 0
        self.is_noisy_mode = self.setup_arguments().parse_args().noisy_mode

        self.listener = self.setup_communication()
        self.connection = None
        self.start_time = None
        self.next_drop_timestamp = None

    def ready_for_connections(self):
        self.connection = self.listener.accept()

    @staticmethod
    def setup_arguments() -> ArgumentParser:
        arg_parser = ArgumentParser(description='Vector processing application')
        arg_parser.add_argument(
            '-n', '--noisy-mode', action='store_const', dest='noisy_mode', const='True', help='enable noisy mode'
        )
        return arg_parser

    @staticmethod
    def generate_vectors(vectors_count):
        # TODO: convert this into a single list object
        vectors = []
        for j in range(vectors_count):
            vector = []
            for i in range(50):
                vector.append(numpy.random.normal())

            vectors.append(vector)
        return vectors

    @staticmethod
    def setup_communication():
        address = (SERVER_HOST, SERVER_PORT)
        return Listener(address, authkey=SERVER_AUTH_KEY)

    def is_noise(self):
        return self.is_noisy_mode and time.time() >= self.next_drop_timestamp

    def send_vectors(self, vectors_count):
        if vectors_count == 0:
            return

        vectors = VectorGenerator.generate_vectors(vectors_count)
        self.connection.send(vectors)
        self.sent_vectors_count += vectors_count

    def set_next_drop_timestamp(self, now):
        self.next_drop_timestamp = now + numpy.random.uniform(low=2, high=3)

    def rate_check(self):
        rate, duration = self.calculate_send_rate()
        while rate > VECTORS_PER_SECOND:
            rate, duration = self.calculate_send_rate()

        # if rate < VECTORS_PER_SECOND:
        #     missing_rate = (VECTORS_PER_SECOND - rate) / VECTORS_PER_SECOND
        #     missing_vectors_count = int(missing_rate * duration)
        #     if missing_vectors_count > 0:
        #         print(f'count: {missing_vectors_count}')
        #         exit()

            # self.send_vectors(missing_vectors_count)

    def calculate_send_rate(self):
        now = time.time()
        duration = now - self.start_time
        rate = self.sent_vectors_count / duration
        print(f'current rate (from server): {rate}')
        return rate, duration


def start():
    vector_generator.start_time = time.time()
    if vector_generator.is_noisy_mode:
        vector_generator.set_next_drop_timestamp(vector_generator.start_time)


if __name__ == '__main__':
    vector_generator = VectorGenerator()
    vector_generator.ready_for_connections()
    msg = vector_generator.connection.recv()

    start()

    if msg != 'start':
        # todo gracefully handle other msgs as error
        raise RuntimeError()

    while True:
        if vector_generator.is_noise():
            vector_generator.sent_vectors_count += 1
            vector_generator.set_next_drop_timestamp(time.time())
            continue

        vector_generator.send_vectors(1)

        if vector_generator.sent_vectors_count % 10 == 0:
            vector_generator.rate_check()
