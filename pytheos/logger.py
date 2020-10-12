#!/usr/bin/env python
import logging


def init_logger():
    logger = logging.getLogger('pytheos')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('pytheos.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


Logger = init_logger()
