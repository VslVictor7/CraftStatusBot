# Minecraft Server Status Bot

- Um bot do Discord funcional feito por mim mesmo para cobrir um conceito nicho que me atende. Ele possui a principal funcionalidade que é de monitorar um servidor minecraft, mostrando o ip publico da maquina que está rodando o servidor JAVA, o numero de jogadores, nome deles e se o servidor está online.

- Funcionalidade principal de suporte: LOG do servidor minecraft em um chat do discord para melhor monitoramento remoto, além de mostrar em embeds os jogadores que saíram e entraram no servidor (Isso também é registrado no banco de dados).

- Funcionalidades Secundárias: API do GENIUS para busca de letras de musicas, comando para mostrar estatisticas dos jogadores que já jogaram no servidor, limpar chat do servidor e Dm (dm do bot),.

## Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Considerações Importantes](#considerações-importantes)

## Pré-requisitos

- Python 3.8 ou maior
- PostgreSQL
- Docker (opcional)

## Instalação

1. **Clone o repositório** (caso ainda não tenha feito):
```bash
   git clone <https://github.com/VslVictor7/Status-Manager-Bot.git>

   cd Status-Manager-Bot
```

2. **Crie uma Máquina Virtual** (venv):

```bash
  python -m venv venv
```

3. **Ativar Máquina Virtual**:
```bash
  source .venv/scripts/activate
```

4. **Atualizar o pip**
```bash
python -m pip install --upgrade pip
```

5. **Instalar requirements.txt**
```bash
  pip install -r requirements.txt
```

## Configuração

1. **Configurar o arquivo .env**:

- Duplique o arquivo .example-env e renomeie-o para .env (Ou .env.prod se for utilizar do docker-compose-prod).
- Substitua os valores de token, IDs e outros campos conforme necessário.

2. Enviar mensagem inicial do bot:

- O aqruivo .env deve ser configurado corretamente para que a etapa da mensagem placeholder funcione.
  
- Execute o script bot_sender.py para enviar uma mensagem placeholder que será usada como base para atualizar a mensagem com um embed mostrando as informações do servidor Minecraft.
```bash
python bot_sender.py
```
- Não se preocupe, você pode rodar o script normalmente e de forma independente. Contanto que esteja no diretório do arquivo, utilize de 'py bot_sender.py' para rodar o script.

## Execução

- Após configurar o .env e também obter uma mensagem placeholder, execute o bot por meio dos arquivos:

run_message_manager.vbs (Para não ter nenhum terminal aberto ao rodar o bot, interessante caso queira roda-lo em segundo plano)

ou

script.bat (Caso queira ver o terminal normalmente.)

ou

- Caso queira rodar diretamente, execute o main.py:
```bash
python main.py
```

E por fim, caso for rodar em um docker container, leia abaixo:

## Executando com Docker Container

- Certifique-se de que está do diretorio do Dockerfile e dockercompose:

- Certifique-se que .env.prod e requirements.txt também estejam no mesmo diretorio descrito acima:

- após isso, crie a imagem com:

```bash
docker build -t discord-bot .
```
rode o container com:

```bash
docker-compose -f docker-compose-prod.yml up --build
```

## Considerações Importantes

- É NECESSÁRIO UTILIZAR DE POSTGRESQL PARA QUE O BOT RODE O BANCO DE DADOS.

- Arquivo .gitignore: Inclua o nome da pasta da sua venv (por exemplo, venv/ ou .venv/) no .gitignore para evitar conflitos de commits.

- Substituições Necessárias: Certifique-se de substituir os tokens e IDs no arquivo .env para garantir o funcionamento correto do bot.
