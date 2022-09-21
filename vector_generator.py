import time
from multiprocessing.connection import Listener

import numpy as numpy

from Constants import ITEMS_IN_QUEUE, VECTORS_PER_SECOND

vector_queue = []


def generate_vectors():
    for j in range(ITEMS_IN_QUEUE):
        vector = []
        for i in range(50):
            vector.append(numpy.random.normal())

        vector_queue.append(vector)


def send_vectors():
    vectors_to_send = vector_queue[:VECTORS_PER_SECOND]
    del vector_queue[-VECTORS_PER_SECOND:]
    conn.send(vectors_to_send)


def wait_until_bucket_ended():
    now = time.time()
    if now - start_time < 1:
        print(f'sleeping because it only took {now - start_time}')
        time.sleep(start_time + 1 - now)


if __name__ == '__main__':
    generate_vectors()
    address = ('localhost', 6000)
    listener = Listener(address, authkey=b'secret')
    try:
        conn = listener.accept()
        msg = conn.recv()

        while True:
            start_time = time.time()

            if msg == 'get':
                send_vectors()
                wait_until_bucket_ended()

            if msg == 'close':
                conn.close()
                break
    finally:
        listener.close()
