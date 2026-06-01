import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def retry(count = 3):
    def main(func):
        def wrapper(*args, **kwargs):
            for _ in range(count):
                try:
                    logger.info('Starting execution')
                    result = func(*args, **kwargs)
                    logger.info('Execution completed')
                    return result
                except Exception as e:
                    logger.error(f'Error : {e}')
        return wrapper
    return main

@retry(5)
def do_work():
    print(10/0)

do_work()