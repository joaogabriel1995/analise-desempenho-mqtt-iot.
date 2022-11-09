# Locust

Agora, vamos analisar o arquivo locustfile.py e vamos destrinchar o código.
Como podemos analisar o arquivo locust é um módulo Python normal, ele pode importar código de outros arquivos ou pacotes.

## Import

```.py
import time
from locust import User, TaskSet, events, task
import paho.mqtt.client as mqtt
```

Primeiro iremos definir uma classe para os usuários que iremos simular. Essa classe herda da classe User do Locust.

Iremos inicializar essa classe com o nosso método construtor `__init__` e iremos utilizar `super()`, função que nos permite sobrescrever métodos e alterar comportamentos.

## Classe User

```{.py line linenums="1"}
class MQTTLocust(User):
    tasks = {PublishTask}
    _locust_environment = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        self.client_name = "Device - " + str(COUNTClient)
        self.client = mqtt.Client(self.client_name)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_log = self.on_log
        self.client.pubmessage = {}

```

Aqui estamos importando o método init da classe pai, e o sobrescrevendo para adicionar nosso `self.client` que é uma instância de `paho.mqtt.client.Client`, esse cliente MQTT pode ser usado para publicar e receber mensagens. Quando o teste é iniciado, o locust criará uma instância para cada cliente que for simulado. Cada um desses clients será executado em um micro-thread.

O comportamento deste usuário é definido por tarefas que serão definidas mais a frente. Na linha 3 estamos mostrando para nossa classe MQTTLocust as tarefas que nossos clientes executarão.

Nas linhas 10, 11 e 12 foi associada as funções de callback, essas funções são executadas em resposta a algum evento. Irei detalhar cada uma delas abaixo.

## Callbacks MQTT

A função `on_connect` é chamada quando o Broker responde à nossa solicitação de conexão.

```{.py line linenums="1"}
def on_connect(client, userdata, flags, rc, props=None):
    print("Connect ", client)
```

A função `on_publish` é executada quando uma mensagem concluiu a transmissão para o broker. Para mensagens com níveis de QoS 1 e 2, isso significa que as mensagens foram entregues ao broker. Para QoS 0, isso significa simplesmente que a mensagem deixou o cliente.
Na linha 3 da nossa função on_publish iremos capturar o tempo em que a mensagem de confirmação chegou.

Na linha 8 foi vinculado a um evento que é relacionado ao Locust, esse evento é acionado quando uma solicitação é concluida, bem-sucedidade ou malsucedidade. Isso é um modo de informarmos ao locust o fim de uma solicitação, o tempo em que essa solicitação foi finalizada e possibilitando que esses valores sejam apresentadas em uma interface que o Locust possui para visualizar os resultados.

```{.py line linenums="1"}
def on_publish(self, client, userdata, mid):

        self.end_time = get_time("Stop")

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
```

a função on_log é executada quando o cliente tem informações de log. Isso é util para analisarmos os erros.

```{.py line linenums="1"}
def on_log(self, client, userdata, level, buf):
    print(buf)

```

## TaskSet

Classe que define um conjunto de tarefas que um usuário executará.
Aqui iremos definir duas tarefas , uma quando o teste começar os clientes irão conectar ao broker e logo em seguida irão desconecta.
Ja a segunda tarefa que foi definida é mais complexa, nessa tarefa o cliente conectará ao Broker, capturar o tempo logo após a conexão e envia uma mensagem em um tópico específico e após desconecta do broker.

```{.py line linenums="1"}
class PublishTask(TaskSet):
    def on_start(self):
        self.client.connect(host=broker_address, port=1883, keepalive=60)
        self.client.disconnect()

    @task(1)
    def task_pub(self):
        self.client.reconnect()
        self.client.loop_start()
        self.start_time = get_time("Start")
        topic = "Device{}".format(str(self.client._client_id))
        payload = "0123456789" * 2
        MQTTMessageInfo = self.client.publish(topic, payload, qos=1, retain=False)
        pub_mid = MQTTMessageInfo.mid
        print("Mid = " + str(pub_mid))
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
        self.client.disconnect()
        self.client.loop_stop()
        time.sleep(1)

```

Podemos perceber que já definimos os dois tempos que serão utilizados pelo Locust, um tempo que é capturado assim que a mensagem vai ser enviada e um segundo tempo que foi capturado logo após a confirmação de recebimento. Esse segundo tempo é capturado quando a função de callback on_publish é chamada.

Temos uma classe que Message, essa classe fica responsavel por criar um objeto que temos as informações da nossa mensagem.
Isso facilita manipulação da mensagem se for necessário.

```py
class Message(object):
    def __init__(self, type, qos, topic, payload, start_time, timeout, name):
        self.type = (type,)
        self.qos = (qos,)
        self.topic = topic
        self.payload = payload
        self.start_time = start_time
        self.timeout = timeout
        self.name = name
```

Criamos duas funções uma para calcular a diferença de tempo de chegada da nossa mensagem menos o tempo de chegada da nossa mensagem.

```py
def time_delta(t1, t2):
    return int((t2 - t1))
```

```py
def increment():
    global COUNTClient
    COUNTClient = COUNTClient + 1

```

Por últimos irei definir algumas variavéis que iremos utilizar em nosso código.

```py
broker_address = "192.168.15.3"
COUNTClient = 0
REQUEST_TYPE = "MQTT"
PUBLISH_TIMEOUT = 10000

```

Segue abaixo o código completo.

```{.py line linenums="1"}
import time
from locust import User, TaskSet, events, task
import paho.mqtt.client as mqtt

broker_address = "192.168.15.3"
COUNTClient = 0
REQUEST_TYPE = "MQTT"
PUBLISH_TIMEOUT = 10000


def time_delta(t1, t2):
    return int((t2 - t1))


def get_time(context):
    time_info = time.time() * 1000
    print(context, time_info)
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
        self.client.disconnect()

    @task(1)
    def task_pub(self):
        self.client.reconnect()
        self.client.loop_start()
        self.start_time = get_time("Start")
        topic = "Device{}".format(str(self.client._client_id))
        payload = "0123456789" * 2
        MQTTMessageInfo = self.client.publish(topic, payload, qos=1, retain=False)
        pub_mid = MQTTMessageInfo.mid
        print("Mid = " + str(pub_mid))
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
        self.client.disconnect()
        self.client.loop_stop()
        time.sleep(1)


class MQTTLocust(User):
    tasks = {PublishTask}
    _locust_environment = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        self.client_name = "Device - " + str(COUNTClient)
        self.client = mqtt.Client(self.client_name)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_log = self.on_log
        self.client.pubmessage = {}

    def on_connect(client, userdata, flags, rc, props=None):
        print("Connect")

    def on_publish(self, client, userdata, mid):

        self.end_time = get_time("Stop")

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


```

Agora que já foi explicado as partes mais importantes do código iremos rodar esse comando no terminal.

```title="Shell"

locust -f locustfile.py

```


