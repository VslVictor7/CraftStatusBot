# Minecraft Server Status Bot

Este bot atualiza automaticamente uma mensagem com o status do servidor de Minecraft em tempo real. Siga os passos abaixo para configurar e iniciar o bot.

## Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Considerações Importantes](#considerações-importantes)

## Pré-requisitos

- Python 3.x
- Biblioteca `venv` (instalada por padrão com Python 3)

## Instalação

1. **Clone o repositório** (caso ainda não tenha feito):
```bash
   git clone <https://github.com/VslVictor7/Minecraft-Server-Status-Manager.git>

   cd Minecraft-Server-Status-Manager
```

2. **Crie uma Máquina Virtual** (venv):

```bash
  python -m venv venv
```
Ou
```bash
  python -m venv .venv
```

3. **Ativar Máquina Virtual**:
```bash
  source .venv/Scripts/activate
```

4. **Instalar requirements.txt**
```bash
  pip install -r requirements.txt
```

## Configuração

1. **Configurar o arquivo .env**:

- Duplique o arquivo .example-env e renomeie-o para .env.
- Substitua os valores de token, IDs e outros campos conforme necessário.

2. Enviar mensagem inicial do bot:

- Execute o script bot_sender.py para enviar uma mensagem placeholder que será usada nas atualizações de status do servidor:
```bash
python bot_sender.py
```

## Execução

- Após configurar o .env, execute o bot por meio dos arquivos:

run_message_manager.vbs

ou

script.bat

- Caso queira rodar diretamente, execute o main.py:
```bash
python main.py
```


## Considerações Importantes

- Arquivo .gitignore: Inclua o nome da pasta da sua venv (por exemplo, venv/ ou .venv/) no .gitignore para evitar conflitos de commits.

- Substituições Necessárias: Certifique-se de substituir os tokens e IDs no arquivo .env para garantir o funcionamento correto do bot.