import datetime
import time
from multiprocessing.connection import Client

import numpy

from Constants import GET_VECTORS_MESSAGE, SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY, INTERVAL_IN_SECONDS, \
    VECTORS_IN_MATRIX, LOG_FILE_PATH
from StatisticsLogger import ResultsLogger


def get_client():
    address = (SERVER_HOST, SERVER_PORT)
    return Client(address, authkey=SERVER_AUTH_KEY)


if __name__ == '__main__':
    resultsLogger = ResultsLogger(LOG_FILE_PATH)

    connection = get_client()
    vector_acquisition_rates = []
    start_time = time.time()
    try:
        while True:
            iteration_start = time.time()
            now = time.time()
            connection.send(GET_VECTORS_MESSAGE)
            vectors = connection.recv()
            time_passed = time.time() - now
            if time_passed > 1:
                current_date_and_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print(f'[{current_date_and_time}] Warning: Seems like a packet was lost in transit')
            vector_acquisition_rate = len(vectors) / time_passed
            vector_acquisition_rates.append(vector_acquisition_rate)

            while len(vectors) > 0:
                vectors_chunk = vectors[:VECTORS_IN_MATRIX]
                del vectors[:VECTORS_IN_MATRIX]
                mean = numpy.mean(vectors_chunk)
                std_deviation = numpy.std(vectors_chunk)
                resultsLogger.log_matrix_statistics(mean, std_deviation)

            if start_time + INTERVAL_IN_SECONDS <= time.time():
                break

    finally:
        acquisition_rate_mean = numpy.mean(vector_acquisition_rates)
        acquisition_rate_std = numpy.std(vector_acquisition_rates)

        resultsLogger.log_acquisition_rate_statistics(
            vector_acquisition_rates, acquisition_rate_mean, acquisition_rate_std
        )

        connection.close()

