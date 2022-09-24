import subprocess
import sys
import time
import unittest

from Constants import VECTOR_LENGTH, EXPECTED_VECTORS_PER_SECOND, GET_VECTORS_MESSAGE
from VectorGenerator import VectorGenerator


class VectorGeneratorTest(unittest.TestCase):
    def testVectorGeneratorSanityWithNoise(self):
        VectorGeneratorTest.start_vector_generator(noisy_mode=True)
        client = VectorGenerator.get_client()
        try:
            self.start_sanity_test(client)
        finally:
            client.close()

    def testVectorGeneratorSanity(self):
        VectorGeneratorTest.start_vector_generator(noisy_mode=False)
        client = VectorGenerator.get_client()
        try:
            self.start_sanity_test(client)
        finally:
            client.close()

    @staticmethod
    def start_vector_generator(noisy_mode: bool):
        if noisy_mode:
            subprocess.Popen(['python3', 'VectorGenerator.py', '-n'])
        else:
            subprocess.Popen(['python3', 'VectorGenerator.py'])
        time.sleep(3)

    def start_sanity_test(self, client):
        expected_rate_upper_limit_factor = 1.01
        expected_rate_lower_limit_factor = 0.99

        requests_counter = 0
        start_time = time.time()
        client.send(GET_VECTORS_MESSAGE)

        while True:
            msg = client.recv()
            self.validate_msg(msg)
            requests_counter += 1

            now = time.time()

            # Give a 1-second warmup for the rate to stabilize
            if now - start_time >= 1:
                duration = now - start_time
                self.log_statistics(duration, requests_counter)
                self.validate_rate(
                    duration, expected_rate_lower_limit_factor, expected_rate_upper_limit_factor, requests_counter
                )

            if now - start_time >= 60:
                break

    @staticmethod
    def log_statistics(duration, requests_counter):
        print(f'[{int(time.time())}] Received {requests_counter} vectors in {duration:.2f} seconds, '
              f'which is a rate of {requests_counter / duration}')

    def validate_rate(self, duration, expected_rate_lower_limit_factor, expected_rate_upper_limit_factor,
                      requests_counter):
        recv_rate = requests_counter / duration
        self.assertLessEqual(recv_rate, EXPECTED_VECTORS_PER_SECOND * expected_rate_upper_limit_factor)
        self.assertGreaterEqual(recv_rate, EXPECTED_VECTORS_PER_SECOND * expected_rate_lower_limit_factor)

    def validate_msg(self, msg):
        self.assertIsInstance(msg, list)
        self.assertIsInstance(msg[0], float)
        self.assertEquals(len(msg), VECTOR_LENGTH)

    def setUp(self):
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter("ignore")


if __name__ == '__main__':
    unittest.main()
