import time
COUNTClient: int = 0


def time_delta(t1, t2):
    return int((t2 - t1))


def get_time(context):
    time_info = time.time() * 1000
    # print(context, time_info)
    return time_info


def formatpayload(SIZE_PAYLOAD):
    payload = "0" * SIZE_PAYLOAD
    return payload


def increment():
    global COUNTClient
    COUNTClient = COUNTClient + 1
