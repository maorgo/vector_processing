import time
from argparse import ArgumentParser
from multiprocessing.connection import Listener

import numpy as numpy

from Constants import ITEMS_IN_QUEUE, VECTORS_PER_SECOND, SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY

vector_queue = []


def setup_arguments() -> ArgumentParser:
    arg_parser = ArgumentParser(description='Vector processing application')
    arg_parser.add_argument(
        '-n', '--noisy-mode', action='store_const', dest='noisy_mode', const='True', help='enable noisy mode'
    )
    return arg_parser


def generate_vectors():
    for j in range(ITEMS_IN_QUEUE):
        vector = []
        for i in range(50):
            vector.append(numpy.random.normal())

        vector_queue.append(vector)


def send_vectors():
    vectors_to_send = vector_queue[:VECTORS_PER_SECOND]
    del vector_queue[:VECTORS_PER_SECOND]
    conn.send(vectors_to_send)


def wait_until_bucket_ended():
    now = time.time()
    if now - start_time < 1:
        time.sleep(start_time + 1 - now)


def should_drop_vectors(drop_time):
    now = time.time()
    if int(now) == int(drop_time):
        print('Dropping packet due to noise')
        return True

    return False


if __name__ == '__main__':
    parser = setup_arguments()
    generate_vectors()
    address = (SERVER_HOST, SERVER_PORT)
    listener = Listener(address, authkey=SERVER_AUTH_KEY)
    try:
        noisy_mode_enabled = parser.parse_args().noisy_mode
        conn = listener.accept()
        msg = conn.recv()
        next_drop_time = time.time() + numpy.random.uniform(low=2, high=3)

        while True:
            start_time = time.time()

            if msg == 'get':
                if noisy_mode_enabled:
                    if should_drop_vectors(next_drop_time):
                        # Skip the current bucket as it is noise
                        time.sleep(1)
                        next_drop_time = time.time() + numpy.random.uniform(low=2, high=3)
                        continue

                send_vectors()
                wait_until_bucket_ended()

            # if start_time + INTERVAL_IN_SECONDS + GRACE_PERIOD_SECONDS >= time.time():
            #     conn.close()
            #     break
    finally:
        listener.close()
