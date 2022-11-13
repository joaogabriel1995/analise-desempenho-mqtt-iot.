# Locust

Agora, vamos analisar o arquivo locustfile.py e vamos destrinchar o código.
Como podemos analisar o arquivo locust é um módulo Python normal, ele pode importar código de outros arquivos ou pacotes.

Nesse primeiro momento irei explicar os códigos e resultados para os testes sem a utilização do protocolo de segurança `Transport Layer Security`(TLS)

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
    wait_time = constant(WAIT_TIME)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        self.client_name = "Device - " + str(COUNTClient)
        self.client = mqtt.Client(self.client_name)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.pubmessage = {}

```

Aqui estamos importando o método init da classe pai, e o sobrescrevendo para adicionar nosso `self.client` que é uma instância de `paho.mqtt.client.Client`, esse cliente MQTT pode ser usado para publicar e receber mensagens. Quando o teste é iniciado, o locust criará uma instância para cada cliente que for simulado. Cada um desses clients será executado em um micro-thread.

O comportamento deste usuário é definido por tarefas que serão definidas mais a frente. Na linha 3 estamos mostrando para nossa classe MQTTLocust as tarefas que nossos clientes executarão.

Nas linhas 11 e 12 foi associada as funções de callback, essas funções são executadas em resposta a algum evento. Irei detalhar cada uma delas abaixo.

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
```

## TaskSet

Classe que define um conjunto de tarefas que um usuário executará.
Aqui iremos definir duas tarefas , uma quando o teste começar os clientes irão conectar ao broker e logo em seguida irão desconecta.
Ja a segunda tarefa que foi definida é mais complexa, nessa tarefa o cliente conectará ao Broker, capturar o tempo logo após a conexão e envia uma mensagem em um tópico específico e após desconecta do broker.

```{.py line linenums="1"}
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

    def on_stop(self):
        global COUNTClient
        COUNTClient = 0
        return super().on_stop()

```

Podemos perceber que já definimos os dois tempos que serão utilizados pelo Locust, um tempo que é capturado assim que a mensagem vai ser enviada e um segundo tempo que foi capturado logo após a confirmação de recebimento. Esse segundo tempo é capturado quando a função de callback on_publish é chamada.

## Class Message

Temos uma classe que Message, essa classe fica responsavel por criar um objeto que temos as informações da nossa mensagem.
Isso facilita manipulação da mensagem se for necessário. Essa classe ficou alocada no arquivo `message.py`

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

# Utils

Criamos três funções em um arquivo denominado `utils`:

- Uma para calcular a diferença de tempo de chegada da nossa mensagem menos o tempo de chegada da nossa confirmação de entrega.

````py
def time_delta(t1, t2):
    return int((t2 - t1))```

- Uma função responsavel por capturar o tempo em um determinado parte no código.

```py

def get_time():
    time_info = time.time() * 1000
    return time_info
```
- Uma função responsável por formatal o tamanho do nosso payload.

```py

def formatpayload(SIZE_PAYLOAD):
    payload = "0" * SIZE_PAYLOAD
    return payload

````

Por últimos irei definir algumas variavéis que iremos utilizar em nosso código.

```py
broker_address: str = "192.168.15.3"
COUNTClient: int = 0
REQUEST_TYPE: str = "MQTT"
PUBLISH_TIMEOUT: int = 10000
SIZE_PAYLOAD: int = 6
PORT_HOST: int = 1883
WAIT_TIME: int = 1
```

Segue abaixo o código completo.

```{.py line linenums="1" title="locustfile.py"}
import time
from locust import User, TaskSet, events, task, constant
import paho.mqtt.client as mqtt
from utils import get_time, formatpayload, time_delta
from message import Message

broker_address: str = "192.168.15.3"
COUNTClient: int = 0
REQUEST_TYPE: str = "MQTT"
PUBLISH_TIMEOUT: int = 10000
SIZE_PAYLOAD: int = 6
PORT_HOST: int = 1883
WAIT_TIME: int = 1


def increment():
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

    def on_stop(self):
        global COUNTClient
        COUNTClient = 0
        return super().on_stop()


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
```

```{.py line linenums="1" title="utils.py"}
import time


def time_delta(t1, t2):
    return int((t2 - t1))


def get_time():
    time_info = time.time() * 1000
    return time_info


def formatpayload(SIZE_PAYLOAD):
    payload = "0" * SIZE_PAYLOAD
    return payload


```

```{.py line linenums="1" title="message.py"}
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

Agora que já foi explicado as partes mais importantes do código iremos rodar esse comando no terminal.

```title="Shell"

locust -f locustfile.py

```
