import sys
import logging

def get_log_level(logging_level):
    if logging_level == "DEBUG":
        return logging.DEBUG
    elif logging_level == "ERROR":
        return logging.ERROR
    elif logging_level == "INFO":
        return logging.INFO
    else:
        return logging.INFO

def get_logger(name, logging_level) -> logging.Logger:
    stream_handler = logging.StreamHandler(sys.stdout)
    log = logging.getLogger(name=name)
    log_level = get_log_level(logging_level=logging_level)
    log.setLevel(log_level)
    formatter = logging.Formatter('[%(levelname)s][%(funcName)s][%(lineno)d] : %(message)s')
    stream_handler.setFormatter(formatter)
    if not log.hasHandlers():
        log.addHandler(stream_handler)
    return log
