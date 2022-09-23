import subprocess
import time
from argparse import ArgumentParser

from Constants import INTERVAL_IN_SECONDS


def setup_arguments() -> ArgumentParser:
    arg_parser = ArgumentParser(description='Vector processing application')
    arg_parser.add_argument(
        '-n', '--noisy-mode', action='store_const', dest='noisy_mode', const='True', help='enable noisy mode'
    )
    return arg_parser


if __name__ == '__main__':
    parser = setup_arguments()
    noisy_mode_enabled = parser.parse_args().noisy_mode

    print(f'Starting the generator (server) at {time.strftime("%H:%M:%S")}')
    if noisy_mode_enabled:
        a = subprocess.Popen(['python3', 'VectorGenerator.py', '-n'])
    else:
        a = subprocess.Popen(['python3', 'VectorGenerator.py'])

    # grace period to let the server start
    time.sleep(3)

    print('Starting the processor (client)')
    b = subprocess.Popen(['python3', 'VectorProcessor.py'])

    # This is the duration of the application life
    time.sleep(INTERVAL_IN_SECONDS)
    b.communicate()
