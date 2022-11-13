import time
from locust import User, TaskSet, events, task, constant
import paho.mqtt.client as mqtt
import ssl
from Locust.src.utils import get_time, increment, formatpayload, time_delta
from message import Message


broker_address = "192.168.15.3"
COUNTClient = 0
REQUEST_TYPE = "MQTT"
PUBLISH_TIMEOUT = 10000
SIZE_PAYLOAD = 256
PORT_HOST = 8883
WAIT_TIME: int = 1


def increment(var):
    global COUNTClient
    COUNTClient = COUNTClient + 1


class PublishTask(TaskSet):
    def on_start(self):
        self.client.connect(host=broker_address, port=PORT_HOST, keepalive=60)

    @task(1)
    def task_pub(self):
        self.client.loop_start()
        self.start_time = get_time()
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


class MQTTLocust(User):
    tasks = {PublishTask}
    _locust_environment = None
    wait_time = constant(WAIT_TIME)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        self.client_name = "Device - " + str(COUNTClient)
        self.client = mqtt.Client(self.client_name)
        self.client.tls_set("/home/joao/Desenvolvimento/tcc/docker/certificadoSSL/ca.crt",
                            tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.tls_insecure_set(True)

        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        #self.client.on_log = self.on_log
        self.client.pubmessage = {}

    def on_connect(client, userdata, flags, rc, props=None):
        print("Connect")

    def on_publish(self, client, userdata, mid):

        self.end_time = get_time()
        mid = "{}-{}".format(mid,
                             self.client_name)

        message = client.pubmessage.pop(mid, None)
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
