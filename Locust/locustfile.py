import time
from locust import User, TaskSet, events, task, constant
import paho.mqtt.client as mqtt

broker_address = "192.168.15.3"
COUNTClient = 0
REQUEST_TYPE = "MQTT"
PUBLISH_TIMEOUT = 10000


def time_delta(t1, t2):
    return int((t2 - t1))


def get_time(context):
    time_info = time.time() * 1000
    # print(context, time_info)
    return time_info


def increment():
    global COUNTClient
    COUNTClient = COUNTClient + 1


class Message(object):
    def __init__(self, type, qos, topic, payload, start_time, timeout, name):
        self.type = (type,)
        self.qos = (qos,)
        self.topic = topic
        self.payload = payload
        self.start_time = start_time
        self.timeout = timeout
        self.name = name


class PublishTask(TaskSet):
    def on_start(self):
        self.client.connect(host=broker_address, port=1883, keepalive=60)

    @task(1)
    def task_pub(self):
        self.client.loop_start()
        self.start_time = get_time("Start")
        topic = "Device{}".format(str(self.client._client_id))
        payload = "0" * 256
        MQTTMessageInfo = self.client.publish(
            topic, payload, qos=1, retain=False)
        pub_mid = "{}-{}".format(MQTTMessageInfo.mid,
                                 self.client._client_id.decode())
        MQTTMessageInfo.mid = "{}-{}".format(MQTTMessageInfo.mid,
                                             self.client._client_id.decode())
        print(MQTTMessageInfo.mid, pub_mid)
        self.client.user_data_set(pub_mid)

        self.client.pubmessage[pub_mid] = Message(
            REQUEST_TYPE,
            1,
            topic,
            payload,
            self.start_time,
            PUBLISH_TIMEOUT,
            str(self.client._client_id),
        )
        MQTTMessageInfo.wait_for_publish()

        self.client.loop_stop()
        constant(1)


class MQTTLocust(User):
    tasks = {PublishTask}
    _locust_environment = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        self.client_name = "Device - " + str(COUNTClient)
        self.client = mqtt.Client(self.client_name, userdata="")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        #self.client.on_log = self.on_log
        self.client.pubmessage = {}

    def on_connect(client, userdata, flags, rc, props=None):
        print("Connect")

    def on_publish(self, client, userdata, mid):

        self.end_time = get_time("Stop")
        mid = "{}-{}".format(mid,
                             self.client_name)

        message = client.pubmessage.pop(mid, None)
        print(userdata)
        total_time = time_delta(message.start_time, self.end_time)
        # print(total_time)
        events.request.fire(
            request_type=REQUEST_TYPE,
            name="{}".format(str(self.client_name)),
            response_time=total_time,
            response_length=len(message.payload),
            response=None,
            context={},
            exception=None,
            start_time=message.start_time,
            url=None,
        )

    def on_log(self, client, userdata, level, buf):
        print(buf)
