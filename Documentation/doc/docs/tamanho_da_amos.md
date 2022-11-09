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

No.,"Time","Source","Destination","Protocol","Length","Info"
164,"6.773386734","192.168.15.4","192.168.15.3","MQTT","90","Connect Command"
165,"6.773478368","192.168.15.4","192.168.15.3","MQTT","68","Disconnect Req"
170,"6.776183681","192.168.15.4","192.168.15.3","MQTT","90","Connect Command"
171,"6.776305141","192.168.15.3","192.168.15.4","MQTT","70","Connect Ack"
176,"6.778768225","192.168.15.4","192.168.15.3","MQTT","171","Publish Message (id=1) [Deviceb'Device - 1']"
177,"6.779113569","192.168.15.3","192.168.15.4","MQTT","70","Connect Ack"
180,"6.781291543","192.168.15.3","192.168.15.4","MQTT","70","Publish Ack (id=1)"
182,"6.781571524","192.168.15.4","192.168.15.3","MQTT","68","Disconnect Req"
198,"7.785566016","192.168.15.4","192.168.15.3","MQTT","90","Connect Command"
200,"7.788460087","192.168.15.4","192.168.15.3","MQTT","171","Publish Message (id=2) [Deviceb'Device - 1']"
201,"7.788832923","192.168.15.3","192.168.15.4","MQTT","70","Connect Ack"
```

Após realizarmos a simulação vamos começar a analisar nosso script em python para tratarmos e estudarmos os dados.

## Tratamento dos dados

Primeiro iremos realizar as importações necessárias para que nosso script execute perfeitamente.

```python
import pandas as pd
import re
import matplotlib.pyplot as plt
import scipy
import numpy as np
```

Nesse trecho de código iremos utilizar a biblioteca pandas para ler nossos dados no formato csv e iremos capturar apenas as 5 primeiras linhas para analisarmos como estão nossos dados.

```python
data = pd.read_csv("./amostra_piloto.csv")
data.head(5)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>No.</th>
      <th>Time</th>
      <th>Source</th>
      <th>Destination</th>
      <th>Protocol</th>
      <th>Length</th>
      <th>Info</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>164</td>
      <td>6.773387</td>
      <td>192.168.15.4</td>
      <td>192.168.15.3</td>
      <td>MQTT</td>
      <td>90</td>
      <td>Connect Command</td>
    </tr>
    <tr>
      <th>1</th>
      <td>165</td>
      <td>6.773478</td>
      <td>192.168.15.4</td>
      <td>192.168.15.3</td>
      <td>MQTT</td>
      <td>68</td>
      <td>Disconnect Req</td>
    </tr>
    <tr>
      <th>2</th>
      <td>170</td>
      <td>6.776184</td>
      <td>192.168.15.4</td>
      <td>192.168.15.3</td>
      <td>MQTT</td>
      <td>90</td>
      <td>Connect Command</td>
    </tr>
    <tr>
      <th>3</th>
      <td>171</td>
      <td>6.776305</td>
      <td>192.168.15.3</td>
      <td>192.168.15.4</td>
      <td>MQTT</td>
      <td>70</td>
      <td>Connect Ack</td>
    </tr>
    <tr>
      <th>4</th>
      <td>176</td>
      <td>6.778768</td>
      <td>192.168.15.4</td>
      <td>192.168.15.3</td>
      <td>MQTT</td>
      <td>171</td>
      <td>Publish Message (id=1) [Deviceb'Device - 1']</td>
    </tr>
  </tbody>
</table>
</div>

Para calcularmos o Round Trip Time precisamos capturar as linhas que possuem a informação `Publish Message` e as linhas que apresentão a confirmação de entrega de entrega que são as linhas que possuem a infromação `Publish Ack`.

Dentro desse `for` iremos percorrer nossa tabela de dados amostrais e buscar por essas duas informações que foram explicadas acima. E iremos salvar isso em uma estrutura de dados que são as listas.

```python
array_publish = []
array_publish_ack = []

for i in range(len(data)):
    if re.search("Publish Message", data.loc[i, "Info"]):
        array_publish.append(i)
    if re.search("Publish Ack ", data.loc[i, "Info"]):
        array_publish_ack.append(i)

```

Agora iremos construir um novo Tabela contendo as listas que foram capturadas acima, podemos perceber que em nossa coluna de informações tambem temos os id relacionadas as mensagens trocadas, iremos capturar esses IDs e iremos coloca-los como index da nossa tabela para facilitarmos a manipulação das tabelas.

O primeiro `for` irá realizar os procedimentos para a lista de Publish e o segundo será responsável por realizar os procedimentos para a lista de ACK.

```python
RTT = pd.DataFrame(columns=["Time_publish", "Time_ack"])
for i in array_publish:
    init = re.search("id=", data.loc[i, "Info"]).span()[1]
    end = re.search("\)", data.loc[i, "Info"]).span()[0]
    index = data.loc[i, "Info"][init:end]
    RTT.loc[index,"Time_publish"]  = float(data.loc[i, "Time"])


for i in array_publish_ack:
    init = re.search("id=", data.loc[i, "Info"]).span()[1]
    end = re.search("\)", data.loc[i, "Info"]).span()[0]
    index = data.loc[i, "Info"][init:end]
    RTT.loc[index,"Time_ack"]  = float(data.loc[i, "Time"])

```

Agora que já temos os dados de envio e de entrada iremos calcular a diferença de tempo entre o envio e a confirmação de envio.

```python
RTT["RTT"]  =(RTT["Time_ack"] - RTT["Time_publish"] )* 1000
```

Vamos analisar as 5 primeiras linhas da nossa tabela referente ao `Round Trip Time`.

```python
RTT.head(5)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Time_publish</th>
      <th>Time_ack</th>
      <th>RTT</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>6.778768</td>
      <td>6.781292</td>
      <td>2.523318</td>
    </tr>
    <tr>
      <th>2</th>
      <td>7.78846</td>
      <td>7.790911</td>
      <td>2.450871</td>
    </tr>
    <tr>
      <th>3</th>
      <td>8.798941</td>
      <td>8.801384</td>
      <td>2.443157</td>
    </tr>
    <tr>
      <th>4</th>
      <td>9.809386</td>
      <td>9.81185</td>
      <td>2.464106</td>
    </tr>
    <tr>
      <th>5</th>
      <td>10.828649</td>
      <td>10.840241</td>
      <td>11.592292</td>
    </tr>
  </tbody>
</table>
</div>
</br>

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

### Calculando a desvio padrão $s$

```python
s = RTT["RTT"].std()
s
```

$$
s = 9.329458861571394
$$

### Calculando o Erro

Voltando ao nosso script teremos que adicionar as seguintes linhas de código para calcularmos o tamanho amostral

```python
media = RTT["RTT"].mean()
e = 0.05 * media
e
```

$$
e = 0.2284361217568699
$$

### Calculando o tamanho da nossa amostra

```python
n = (z * (s/e))**2
n
```

$$
n = 6407.366013790879
$$

Com isso finalizamos o calculo do número de amostra que iremos utilizar para nosso estudo.
Lembrando que todos os códigos estaram disponiveis no github.
