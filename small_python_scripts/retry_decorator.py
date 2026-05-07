import time

def retry(count = 3, delay = 0):
    def main(func):
        def wrapper(*args, **kwargs):
            for i in range(count):
                time.sleep(delay)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(e)
        return wrapper
    return main
    
@retry(count=3, delay=1)
def hello():
    print(10/0)
    
hello()