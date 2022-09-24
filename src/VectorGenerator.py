import time
from argparse import ArgumentParser
from multiprocessing.connection import Listener

import numpy as numpy

from Constants import SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY, VECTORS_PER_SECOND, VECTOR_LENGTH, GET_VECTORS_MESSAGE


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
    def generate_vector():
        vector = []
        for i in range(VECTOR_LENGTH):
            vector.append(numpy.random.normal())

        return vector

    @staticmethod
    def setup_communication():
        address = (SERVER_HOST, SERVER_PORT)
        return Listener(address, authkey=SERVER_AUTH_KEY)

    def is_noise(self):
        return self.is_noisy_mode and time.time() >= self.next_drop_timestamp

    def send_vector(self):
        generated_vector = VectorGenerator.generate_vector()
        self.connection.send(generated_vector)
        self.sent_vectors_count += 1

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

    if msg != GET_VECTORS_MESSAGE:
        raise RuntimeError(f"VectorGenerator only supports the 'start' message. Got unrecognized keyword '{msg}'")

    try:
        while True:
            if vector_generator.is_noise():
                vector_generator.sent_vectors_count += 1
                vector_generator.set_next_drop_timestamp(time.time())
                continue

            vector_generator.send_vector()

            if vector_generator.sent_vectors_count % 10 == 0:
                vector_generator.rate_check()
    finally:
        vector_generator.connection.close()
