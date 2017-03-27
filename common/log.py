import os
import json
import logging.config
import time

def setup_logging(
    default_path='./common/config.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def timeit(method):
    """measuring the execution time of methods"""
    def timed(*args, **kw):
        """measuring the execution time of methods"""
        time_start = time.time()
        result = method(*args, **kw)
        time_end = time.time()
        logger.info('%r: %2.2f sec' % \
              (method.__name__, time_end-time_start))
        return result
    return timed