import logging
import time

def log_api(function):
    def log_function(*args, **kwargs):
        logging.info(f'*****User invoked the {function.__name__} function*****')
        print(f'*****User invoked the {function.__name__} function*****')

        start = time.time()
        results = function(*args, **kwargs)
        end = time.time()

        logging.info(f'{function.__name__} took {end - start} seconds')
        print(f'{function.__name__} took {end - start} seconds')
        return results
    
    # Renaming the function name:
    log_function.__name__ = function.__name__
    return log_function