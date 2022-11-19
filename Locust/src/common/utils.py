import time


def time_delta(t1, t2):
    return int((t2 - t1))


def get_time():
    time_info = time.time() * 1000
    return time_info


def formatpayload(SIZE_PAYLOAD):
    payload = "0" * SIZE_PAYLOAD
    return payload

