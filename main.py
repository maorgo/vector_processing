import subprocess
from argparse import ArgumentParser
import time

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
    print(f'is noisy mode enabled: {noisy_mode_enabled}')

    print('Starting the generator (server)')
    a = subprocess.Popen(['python3', 'vector_generator.py'])

    # grace period to let the server start
    time.sleep(2)

    print('Starting the processor (client)')
    b = subprocess.Popen(['python3', 'vector_processor.py'])

    # This is the duration of the transfer
    time.sleep(INTERVAL_IN_SECONDS)
