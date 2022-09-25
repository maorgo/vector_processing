import time
from argparse import ArgumentParser
from multiprocessing.connection import Listener, Client

import numpy as numpy

from Constants import SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY, VECTOR_LENGTH, GET_VECTORS_MESSAGE


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

    def should_introduce_noise(self):
        return self.is_noisy_mode and time.time() >= self.next_drop_timestamp

    def send_vector(self):
        generated_vector = VectorGenerator.generate_vector()
        self.connection.send(generated_vector)
        self.sent_vectors_count += 1

    def set_next_drop_timestamp(self, now):
        self.next_drop_timestamp = now + numpy.random.uniform(low=2, high=3)

    @staticmethod
    def get_client():
        address = (SERVER_HOST, SERVER_PORT)
        return Client(address, authkey=SERVER_AUTH_KEY)

    def start(self):
        self.start_time = time.time()
        if self.is_noisy_mode:
            self.set_next_drop_timestamp(vector_generator.start_time)

        if msg != GET_VECTORS_MESSAGE:
            raise RuntimeError(f"VectorGenerator only supports the 'start' message. Got unrecognized keyword '{msg}'")

        try:
            prev_interval = get_time_as_ms()
            while True:
                interval_start = get_time_as_ms()
                # Only send on a new ms interval
                while interval_start == prev_interval:
                    interval_start = get_time_as_ms()

                prev_interval = interval_start

                # If noise should be introduced, skip the transport of 1 vector
                if vector_generator.should_introduce_noise():
                    vector_generator.sent_vectors_count += 1
                    vector_generator.set_next_drop_timestamp(time.time())
                    continue

                vector_generator.send_vector()

        finally:
            vector_generator.connection.close()


def get_time_as_ms():
    return int(time.time() * 1000)


if __name__ == '__main__':
    vector_generator = VectorGenerator()
    vector_generator.ready_for_connections()
    msg = vector_generator.connection.recv()

    vector_generator.start()
