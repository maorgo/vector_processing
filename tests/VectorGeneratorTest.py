import subprocess
import time
from multiprocessing.connection import Client
import unittest

from src.Constants import SERVER_HOST, SERVER_PORT, SERVER_AUTH_KEY, GET_VECTORS_MESSAGE, VECTORS_PER_SECOND


class VectorGeneratorTest(unittest.TestCase):
    @staticmethod
    def get_VectorGenerator_client():
        subprocess.Popen(['python3', '../VectorGenerator.py', '-n'])
        time.sleep(3)

        address = (SERVER_HOST, SERVER_PORT)
        return Client(address, authkey=SERVER_AUTH_KEY)

    def testVectorGeneratorSanityWithNoise(self):
        expected_rate_upper_limit_factor = 1.01
        expected_rate_lower_limit_factor = 0.99

        client = VectorGeneratorTest.get_VectorGenerator_client()
        requests_counter = 0
        start_time = time.time()
        client.send(GET_VECTORS_MESSAGE)

        while True:
            msg = client.recv()
            self.assertIsInstance(msg, list)
            self.assertIsInstance(msg[0], list)
            requests_counter += 1

            now = time.time()

            # Give a 1-second warmup for the rate to stabilize
            if now - start_time >= 1:
                duration = now - start_time
                print(f'[{int(time.time())}] Received {requests_counter} vectors in {duration:.2f} seconds, '
                      f'which is a rate of {requests_counter / duration}')

                recv_rate = requests_counter / duration
                self.assertLessEqual(recv_rate, VECTORS_PER_SECOND * expected_rate_upper_limit_factor)
                self.assertGreaterEqual(recv_rate, VECTORS_PER_SECOND * expected_rate_lower_limit_factor)

            if now - start_time >= 60:
                break

    def testVectorGeneratorSanity(self):
        raise NotImplemented()


if __name__ == '__main__':
    unittest.main()
