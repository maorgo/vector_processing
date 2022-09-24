GET_VECTORS_MESSAGE = 'start'
STOP_SERVER_MESSAGE = 'stop'
INTERVAL_IN_SECONDS = 20
VECTORS_PER_SECOND = 1_000
ITEMS_IN_QUEUE = INTERVAL_IN_SECONDS * VECTORS_PER_SECOND
VECTORS_IN_MATRIX = 100
VECTOR_LENGTH = 50

SERVER_HOST = 'localhost'
SERVER_PORT = 6000
SERVER_AUTH_KEY = b'secret'
GRACE_PERIOD_SECONDS = 1

LOG_FILE_PATH = '../output.log'
