O projeto está disponibilizado no github e qualquer atualização será disponibiliza.

Aqui iremos dar uma breve explicação como está a organização dos diretórios. Segue abaixo os diretórios disponiveis no projeto:

```
.
|-- Data_analytics
|-- Documentation
|-- Locust
|-- README.md
|-- certificadoSSL
|-- mosquitto
`-- mosquittotls

6 directories, 1 file

```

### Data_analytics

Esse Diretório será responsável por armazenar os resultados das simulações e os scripts para tratamento desses dados.

Aqui irei utilizar um padrão de nomenclatura para as pastas, tentando sempre manter a maior organização e uma maior agilidade ao analisarmos os dados. Segue padrão abaixo.

`device-[x]-sizepayload-[y]-lines-[z]`

`x = Será substituído pela quantidade de dispositivos que foram testados.`

`y = Será substituído pelo tamanho do nosso payload.`

`z = Será substituído pela quantidade de mensagens que foram trocadas POR usuário.`

exemplo:

` device-5-sizepayload-6-msg-100`

Nesse exemplo dado acima iremos encontrar os resultados de um teste realizado com 5 devices, um payload de tamanho 6 bytes, e cada um desses usuários realizou 100 publicações.

Exemplo de arquivos encontrados no diretório `Data_analytics/device-5-sizepayload-6-msg-100`.
Explicação de cada um está ao lado dos nomes.

```{title="device-5-sizepayload-6-msg-100"}
|-- Test\ Report\ for\ locustfile.py.html  # Um relatório disponibilizado pelo próprio locust após a simulação.
|-- data.csv                               # Dados capturados pelo Wireshark em formato csv para análise de dados.
|-- data_wireshark.pcapng                  # Dados capturados pelo Wireshark em formato pcapng.
|-- exceptions_1668211736.780954.csv       # Um relatório de possíveis exceções na simulação
|-- failures_1668211735.9747043.csv        # Um relatório de possíveis falhas na simulação
|-- relatorio.ipynb                        # Um jupyterNotebook contendo os scripts utilizados para tratamento de dados da simulação
`-- requests_1668211735.3653195.csv        # Um relatório das requisições

```

### Documentation

Esse diretório foi utilizado para criar a documentação.

```{title="Documentation"}
.
|-- README.txt
|-- docs
|   |-- code.md
|   |-- image
|   |-- index.md
|   |-- path.md
|   `-- tamanho_da_amos.md
|-- mkdocs.yml
`-- requirements.txt

```

Se necessário rodar a documentação seguir o README.txt com todos os passos necessários para a utilização.

### Locust

Esse diretório iremos encontrar os scripts, que foram utilizados para as simulações.

```{title="Locust"}
.
|-- README.txt
|-- requirements.txt
`-- src
    |-- locustfile.py     #Simulação sem tls
    |-- locustfileTLS.py  #Simulação com tls
    |-- message.py        #classe que iremos utilizar dentro dos dois arquivos acima
    `-- utils.py          #funções que iremos utilizar nos dois primeiros arquivos
```

Dentro desse diretório também foi inserido um `README.txt` com algumas instruções de como rodar as simulações.

### mosquitto e mosquittotls

Dentro desses diretórios iremos encontrar os arquivos necessários para configurarmos o broker mqtt, o diretório denominado mosquitto não possui a pasta config/certs, pois não apresenta necessidade, já no mosquittotls iremos necessitar dos certificados.

```{title="mosquittotls"}
|-- config
|   |-- certs
|   |   |-- ca.crt
|   |   |-- ca.key
|   |   |-- ca.srl
|   |   |-- server.crt
|   |   |-- server.csr
|   |   `-- server.key
|   `-- mosquitto.conf
|-- data
|-- docker-compose.yml
`-- log
    `-- mosquitto.log

```
