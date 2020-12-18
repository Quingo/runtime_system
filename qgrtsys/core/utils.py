import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import colorama as cm
import termcolor as tc
from pathlib import Path, PurePath

cm.init()

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL


def quingo_msg(arg, **kwargs):
    print(tc.colored(arg, 'green'), **kwargs)


def quingo_warning(arg, **kwargs):
    print(tc.colored(arg, 'yellow'), **kwargs)


def quingo_err(arg, **kwargs):
    print(tc.colored(arg, 'red'), **kwargs)


FORMATTER = logging.Formatter(
    "%(asctime)s %(name)s %(lineno)d(%(levelname)s): %(message)s", datefmt='%H:%M:%S')
# LOG_FILE = "my_app.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


# def get_file_handler():
#     file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
#     file_handler.setFormatter(FORMATTER)
#     return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    # better to have too much log than not enough
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    # logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
