import time
from locust import User, TaskSet, events, task, constant
import paho.mqtt.client as mqtt
import json

broker_address = "192.168.151.15"
COUNTClient = 0
REQUEST_TYPE = "MQTT"
PUBLISH_TIMEOUT = 10000


def time_delta(t1, t2):
    return int((t2 - t1))


def get_time():
    time_info = time.time() * 1000
    return time_info


def increment():
    global COUNTClient
    COUNTClient = COUNTClient + 1


def formatpayload(idmonitor):

    strformatuv3 = {
        'data': [
            {
                'Params': {
                    "data0": 1,
                    "data1": 10.2,
                    "data2": 1,
                    "data3": 0.1199,
                    "data4": 1,
                    "data5": 0,
                    "data6": 0.1199,
                    "data7": 0,

                },
                '_idDocument': '0',
                '_idHardwareMonitor': '000000004d2575e7',
                '_idMonitored': '00:00:00:00:00:00:00:00:00:20',
                'datetimedata': time.time(),
                'datetimedatasend': time.time(),
                'group': '0',
                'groupstate': '0',
                'typedata': 'machine',
                'createdAt': {'$date': '2020-1206-02T17:50:42.533Z'},
                '_idMonitor': idmonitor,
                'active': True,
                'offset': 0,
            }
        ]
    }
    format_json = json.dumps(strformatuv3)
    return format_json


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
        self.start_time = get_time()
        topic = "DATAMACHINE/UV3".format(self.client.idMonitor)
        payload = formatpayload(5)
        print(payload)
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


class MQTTLocust(User):
    tasks = {PublishTask}
    _locust_environment = None
    wait_time = constant(5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        self.client_name = "DATAMACHINE/UV{}".format(str(COUNTClient))

        self.client = mqtt.Client(self.client_name)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.idMonitor = COUNTClient
        self.client.username_pw_set("admin", "Ap@690#KptLmn8")
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
