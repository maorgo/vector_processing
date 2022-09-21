import time
from multiprocessing.connection import Client

from Constants import GET_VECTORS_MESSAGE

if __name__ == '__main__':
    address = ('localhost', 6000)
    conn = Client(address, authkey=b'secret')

    try:
        now = time.time()
        vectors_count = 0
        while True:
            conn.send(GET_VECTORS_MESSAGE)
            response = conn.recv()
            vectors_count += len(response)
            time_passed = time.time() - now
            print(f'Got {vectors_count} vectors in {time_passed} seconds, which is a rate of {vectors_count / time_passed}')
    finally:
        conn.close()
