Nesse repositório será os códigos que foram utilizados para as simulações.

Pré-requisitos:

- Possuir python3 em seu sistema operacional.

Para rodar o arquivo seguir o seguinte procedimento(linux)

[1] - Clonar o repositório nomeado `Locust` em seu computador.

[2] - Dentro do Diretório `Locust` executar o seguinte comando

```
python -m venv venv
```
Esse comando irá criar um ambiente virtual, possibilitando que o projeto seja executado conforme o esperado.

[3] - Agora iremos ativar nosso ambiente virtual, lembrando que após poderemos desativar com um simples comando. 

```
source venv/bin/activate
```
[4] - Agora iremos instalar as bibliotecas necessárias para que o projeto seja executado.

```
pip install -r requirements.txt
```
Exemplo de como executar uma simualação. No terminal executar o seguinte comando, lembre de verificar se está dentro do Diretório `Locust`


```
locust -f locustfile.py
```

Esse código vai abrir o navegador e lá poderemos configurar alguns configurações para nosso teste.

Maiores explicações estão disponiveis no Diretório de documentação.