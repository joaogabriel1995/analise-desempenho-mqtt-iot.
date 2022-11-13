import time
from locust import User, TaskSet, events, task, constant
import paho.mqtt.client as mqtt
from utils import get_time, increment, COUNTClient, formatpayload, time_delta


broker_address: str = "192.168.15.3"
COUNTClient: int = 0
REQUEST_TYPE: str = "MQTT"
PUBLISH_TIMEOUT: int = 10000
SIZE_PAYLOAD: int = 6
PORT_HOST: int = 1883
WAIT_TIME: int = 1


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
        self.client.connect(host=broker_address, port=PORT_HOST, keepalive=60)

    @task(1)
    def task_pub(self):
        self.client.loop_start()
        self.start_time = get_time("Start")
        topic = str(self.client._client_id)
        payload = formatpayload(SIZE_PAYLOAD)
        MQTTMessageInfo = self.client.publish(
            topic, payload, qos=1, retain=False)

        pub_mid = "{}-{}".format(MQTTMessageInfo.mid,
                                 self.client._client_id.decode())
        MQTTMessageInfo.mid = "{}-{}".format(MQTTMessageInfo.mid,
                                             self.client._client_id.decode())
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
    wait_time = constant(WAIT_TIME)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        self.client_name = "Device - " + str(COUNTClient)
        self.client = mqtt.Client(self.client_name)
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
        total_time = time_delta(message.start_time, self.end_time)
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
