import time
from multiprocessing.connection import Client

import numpy

from Constants import GET_VECTORS_MESSAGE, SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY, INTERVAL_IN_SECONDS


def get_client():
    address = (SERVER_HOST, SERVER_PORT)
    return Client(address, authkey=SERVER_AUTH_KEY)


if __name__ == '__main__':
    connection = get_client()
    vector_acquisition_rates = []
    start_time = time.time()
    try:
        requests_counter = 0
        while True:
            iteration_start = time.time()
            now = time.time()
            requests_counter += 1
            print(f'requests_counter: {requests_counter}')
            connection.send(GET_VECTORS_MESSAGE)
            vectors = connection.recv()
            time_passed = time.time() - now
            vector_acquisition_rate = len(vectors) / time_passed
            vector_acquisition_rates.append(vector_acquisition_rate)

            print(f'Got {len(vectors)} vectors in {time_passed:.5f} seconds, '
                  f'which is a rate of {vector_acquisition_rate:.2f} vectors per second.')

            while len(vectors) > 0:
                vectors_chunk = vectors[:100]
                del vectors[-100:]
                median = numpy.median(vectors_chunk)
                std_deviation = numpy.std(vectors_chunk)

            if start_time + INTERVAL_IN_SECONDS <= time.time():
                break

    finally:
        connection.close()

        print('******************')
        print(f'acquisition rates: {vector_acquisition_rates}')
        print(f'median: {numpy.median(vector_acquisition_rates)}')
        print(f'std deviation: {numpy.std(vector_acquisition_rates)}')
        print('******************')
