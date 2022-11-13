# DETERMINAÇÃO DO TAMANHO AMOSTRAL

## Introdução

Através de uma pré-amostragem, denominada de amostragem piloto, calcula-se o
número de unidades amostrais necessárias para compor a amostra representativa da população
dentro do limite de erro estipulado ou estabelecido.

Agora que já sabemos rodar o projeto, será realizada uma simulação e serão capituradas as
trocas de mensagens entre o broker e um cliente simulado por nosso projeto.

Lembrando que nossas informações serão capturadas de 2 modos, um que será pelo próprio Locust e um segundo modo será pelo Wireshark para que seja possivel realizar estudos em cima dos nossos dados. Após a obtenção dos dados pelo Wireshark iremos salva-los em formato csv e iremos tratar esses dados em um script em python que também será disponibilizado e explicado mais a frente.

Logo abaixo deixamos uma pequena parte do nosso arquivo da simulação da amostra piloto.

```{.csv title="amostra_piloto.csv"}

"No.","Time","Source","Destination","Protocol","Length","Topic","Message Identifier","Source Port","Destination Port","Info"
"185","26.021096759","192.168.15.4","192.168.15.3","MQTT","90","","","37953","1883","Connect Command"
"187","26.023436459","192.168.15.4","192.168.15.3","MQTT","97","Deviceb'Device - 1'","1","37953","1883","Publish Message (id=1) [Deviceb'Device - 1']"
"188","26.023917838","192.168.15.3","192.168.15.4","MQTT","70","","","1883","37953","Connect Ack"
"191","26.026219616","192.168.15.3","192.168.15.4","MQTT","70","","1","1883","37953","Publish Ack (id=1)"
"198","27.028577195","192.168.15.4","192.168.15.3","MQTT","97","Deviceb'Device - 1'","2","37953","1883","Publish Message (id=2) [Deviceb'Device - 1']"
"200","27.031371904","192.168.15.3","192.168.15.4","MQTT","70","","2","1883","37953","Publish Ack (id=2)"
"212","28.033880087","192.168.15.4","192.168.15.3","MQTT","97","Deviceb'Device - 1'","3","37953","1883","Publish Message (id=3) [Deviceb'Device - 1']"
"214","28.036671599","192.168.15.3","192.168.15.4","MQTT","70","","3","1883","37953","Publish Ack (id=3)"
"220","29.038713357","192.168.15.4","192.168.15.3","MQTT","97","Deviceb'Device - 1'","4","37953","1883","Publish Message (id=4) [Deviceb'Device - 1']"
"221","29.041346621","192.168.15.3","192.168.15.4","MQTT","70","","4","1883","37953","Publish Ack (id=4)"
"235","30.042764932","192.168.15.4","192.168.15.3","MQTT","97","Deviceb'Device - 1'","5","37953","1883","Publish Message (id=5) [Deviceb'Device - 1']"
```

Após realizarmos a simulação vamos começar a analisar nosso script em python para tratarmos e estudarmos os dados.

Nossa amostra piloto ficou salva no seguinte caminho `Data_analytics/device-1-sizepayload-6-msg-600/data.csv`

## Tratamento dos dados

Primeiro iremos realizar as importações necessárias para que nosso script execute perfeitamente.

```python title="relatorio.ipynb"
import pandas as pd
import re
import matplotlib.pyplot as plt
import scipy
import numpy as np
```

Nesse trecho de código iremos utilizar a biblioteca pandas para ler nossos dados no formato csv.

```python title="relatorio.ipynb"
data = pd.read_csv("./data.csv")
ports = data["Source Port"].unique()
ports = ports[ports !=1883]
ports
```

```title="ports"
array([37953])
```

Logo acima capturamos as portas TCP de cada um dos dispositivos. O que nos possibilita separarmos as informações por dispositivo.
Cada um dos valores da lista `ports` representa um dispositivo testado na nossa simulação.Nesse caso em especifico estamos utilizando apenas um dispotivo na porta 37953.

Para calcularmos o Round Trip Time precisamos capturar as linhas que possuem a informação `Publish Message` e as linhas que apresentão a confirmação de entrega que são as linhas que possuem a informação `Publish Ack`.

Logo abaixo iremos capturar as informações necessarias e iremos separar por device e suas respctivas `Publish Message` e `Publish Ack`.

```python title="relatorio.ipynb"
devices = {}
#  : devices será um dicionario que irá ter uma chave referente ao device e o valor será um dataframe referente aos respectivos devices
for port in ports:
  array_publish = data.loc[data["Source Port"] == port].dropna(subset=['Message Identifier'])
  array_publish_ack = data.loc[data["Destination Port"] == port].dropna(subset=['Message Identifier'])
  device = {"publish":array_publish, "publish_ack" : array_publish_ack}
  devices[port] = device

```

Logo abaixo construi uma lógica para utilizarmos as informações dos dados extraidos acima e calculamos o round trip time de cada um dos dispositivos.

```python title="relatorio.ipynb"
data = {}
for port in ports:
    RTT = pd.DataFrame(columns=["Time_publish", "Time_ack"])
    for index, row in devices[port]["publish"].iterrows():
        id = int(row["Message Identifier"])
        time_publish = row["Time"]
        RTT.loc[id, "Time_publish"] = time_publish

    for index, row in devices[port]["publish_ack"].iterrows():
        id = int(row["Message Identifier"])
        time_publish = row["Time"]
        RTT.loc[id, "Time_ack"] = time_publish
    RTT.loc[id, "Time_ack"] = time_publish
    RTT["RTT"]  =(RTT["Time_ack"] - RTT["Time_publish"] )* 1000
    data[port] = RTT

```

Agora já temos calculado todas as linhas de cada um dos dispositivos.

```
data[37953].head()
```

|     | Time_publish | Time_ack  | RTT      |
| --- | ------------ | --------- | -------- |
| 1   | 26.023436    | 26.02622  | 2.783157 |
| 2   | 27.028577    | 27.031372 | 2.794709 |
| 3   | 28.03388     | 28.036672 | 2.791512 |
| 4   | 29.038713    | 29.041347 | 2.633264 |
| 5   | 30.042765    | 30.045957 | 3.19254  |

Agora que analisamos como está nossa tabela depois de todas as manipulações vamos calcular a média, moda, desvio padrão e mais algumas informações. Lembrando que nesse caso estamos tratando os dados de um dispositivo mas o código foi escrito para suportar um ou mais dispositivos.

```.py
i=1
data_mean = []
data_median = []
data_std = []
data_min = []
data_max = []

for port in ports:
  data_mean.append(data[port]["RTT"].mean())
  data_median.append(data[port]["RTT"].mean())
  data_std.append(data[port]["RTT"].mean())
  data_min.append(data[port]["RTT"].mean())
  data_max.append(data[port]["RTT"].mean())

  print("(Device-{})Mean Round Trip Time = {}".format(i ,data[port]["RTT"].mean()))
  print("(Device-{})Median Round Trip Time = {}".format(i ,data[port]["RTT"].median()))
  print("(Device-{})Standard deviation  Round Trip Time = {}".format(i ,data[port]["RTT"].std()))
  print("(Device-{})Min Round Trip Time = {}".format(i ,data[port]["RTT"].min()))
  print("(Device-{})Max Round Trip Time = {}".format(i ,data[port]["RTT"].max()))
  print("---------------------------------------------------------------")

  i+=1

```

```title="output"
(Device-1)Mean Round Trip Time = 2.794579920265673
(Device-1)Median Round Trip Time = 2.6867750000008073
(Device-1)Standard deviation  Round Trip Time = 0.6409882996918244
(Device-1)Min Round Trip Time = 2.37513999991279
(Device-1)Max Round Trip Time = 12.155039000049328
---------------------------------------------------------------



```

## Conceitos básicos de estatística

Para calcularmos o número de amostras precisamos entender alguns conceitos básicos, irei abordar de forma breve para darmos andamento nos calculos.

### Intervalo de confiança

Um intervalo de confiança é uma amplitude de valores, que são derivadas de estatísticas de amostras, que tem a probabilidade de conter o valor de um parâmetro populacional desconhecido.

O **nível de confiança** ($1 - \alpha$) representa a probabilidade de acerto da estimativa. De forma complementar o **nível de significância** ($\alpha$) expressa a probabilidade de erro da estimativa.

O **nível de confiança** representa o grau de confiabilidade do resultado da estimativa estar dentro de determinado intervalo. Quando fixamos em uma pesquisa um **nível de confiança** de 95%, por exemplo, estamos assumindo que existe uma probabilidade de 95% dos resultados da pesquisa representarem bem a realidade, ou seja, estarem corretos.

O **nível de confiança** de uma estimativa pode ser obtido a partir da área sob a curva normal como ilustrado na figura abaixo.

![alt text](https://caelum-online-public.s3.amazonaws.com/1178-estatistica-parte2/01/img007.png)

### Score Z

- É o quanto uma medida se afasta da média em termos de Desvios
  Padrão.
- Quando o escore Z é positivo isto indica que o dado está acima da
  média e quando o mesmo é negativo significa que o dado está abaixo
  da média.
- Seus valores oscilam entre -3 < Z < +3 e isto corresponde a 99,72% da
  área sob a curva da Distribuição Normal.

Em nosso estudo iremos utilizar um nivel de confiança igual a 95% e se consultarmos a tabela de Distribuição normal iremos encontrar um z é aproximadamente 1,96.

Z = 1,96 (tabela da Distribuição Normal)

## Calculando o número de amostra

Para o calculo do número de amostra iremos utilizar a seguinte formula:

$$n = \left(z\frac{s}{e}\right)^2$$

onde:
$z$ = variável normal padronizada

$s$ = desvio padrão amostral

$e$ = erro inferencial

### Calculando o desvio padrão $s$

```python title="relatorio.ipynb"
desvio_padrao_amostral = data[37953]["RTT"].std()
desvio_padrao_amostral
```

$$
desvioPadraoAmostral = 9.329458861571394
$$

### Calculando o Erro

Voltando ao nosso script teremos que adicionar as seguintes linhas de código para calcularmos o tamanho amostral

```python title="relatorio.ipynb"
media = data[37953]["RTT"].mean()
e = 0.05 * media
e
```

$$
e = 0.2284361217568699
$$

### Calculando o tamanho da nossa amostra

```{.py title="relatorio.ipynb"}
n = (z * (s/e))**2
n
```

$$
n = 80.83944240619886
$$

O código que foi explicado acima se localiza no diretório `Data_analytics/device-1-sizepayload-6-msg-600/relatorio.ipynb`

Com isso finalizamos o calculo do número de amostra que iremos utilizar para nosso estudo.
Lembrando que todos os códigos estaram disponiveis no github.
