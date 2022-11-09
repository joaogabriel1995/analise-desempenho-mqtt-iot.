Nesse repositório será disponibilizada como foram realizados os estudos e um breve tutorial de como foram construidos alguns códigos.
Também será disponibilizado alguns conceitos estatísticos que foram utilizados para calcular tamanho de amostras e outros conceitos.

Pré-requisitos:

- Possuir python3 em seu sistema operacional.

Para rodar a documentação seguir o seguinte procedimento(linux)

[1] - Clonar o repositório da documentação em seu computador

[2] - Dentro do Diretório `Documentation` executar o seguinte comando

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

[5] - Vamos entrar dentro do Diretório `doc` e executar o seguinte comando.

```
cd doc
```
[6] - Iniciar o servidor para podermos visualizar a documentação no navegador.

```
mkdocs serve
```