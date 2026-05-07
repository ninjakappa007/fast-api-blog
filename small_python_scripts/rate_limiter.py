import time
import json

def get_redis_instance():
    pass

cache = get_redis_instance()

def rate_limit(max_request, window):
    def deco(func):
        def wrapper(user_id, *args, **kwargs):

            curr_time = time.time()
            data = cache.get(user_id)

            if data:
                old_timestamps = json.loads(data)
            else:
                old_timestamps = []

            timestamps = [ t for t in old_timestamps if curr_time - t < window ]

            if len(timestamps) >= max_request:
                return {
                    "status": 429,
                    "message": "Rate limit exceeded"
                }

            timestamps.append(curr_time)

            cache.set(user_id, json.dumps(timestamps), ex=window)

            return func(user_id, *args, **kwargs)

        return wrapper

    return deco