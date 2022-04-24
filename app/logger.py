import logging
import time


def initialize_logger():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    logging.basicConfig(filename="./logs/log-{}".format(timestr),
                        level=logging.WARNING)


def log_error(error):
    timestamp = time.strftime("%b %d %Y %H:%M:%S")
    logging.error(" [" + timestamp + "]: " + error)
