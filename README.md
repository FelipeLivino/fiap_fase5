# CardioIA — Fase 5

Protótipo acadêmico de assistente cardiológico conversacional. Toda execução
oficial — aplicação, testes, IA generativa e automação — ocorre em contêineres
Docker Compose.

Repositório público: <https://github.com/FelipeLivino/fiap_fase5>

> Use somente cenários fictícios. O CardioIA não diagnostica, não prescreve e
> não substitui profissionais de saúde nem serviços de emergência.

## Estado

- MVP Flask e interface: aprovados no modo mock e no Watson real;
- adapter IBM Watson Assistant v1/v2: implementado; workspace v1 real importado,
  treinado e aprovado em nove casos inéditos;
- Ir Além 1: Gemini 3.5 Flash-Lite, JSON Schema, guardrails, 12 testes offline e
  uma chamada real aprovados;
- Ir Além 2: PostgreSQL, MongoDB e worker RPA com dois ciclos e 13 verificações
  aprovados;
- vídeo demonstrativo real: H.264, 1280 × 720, 30 fps e aproximadamente 46 s;
- pendências externas: nomes/revisores, segunda máquina e aprovação da equipe.

## Pré-requisitos

- Docker Engine/Desktop 28 ou superior;
- Docker Compose v2 com suporte a `--wait`;
- acesso HTTPS para as integrações externas.

Python não precisa estar instalado no host.

## Configuração local

1. Copie `.env.example` para `.env` e mantenha `ASSISTANT_MODE=mock` para o
   fluxo padrão.
2. Crie os arquivos locais necessários em `.secrets/`, seguindo
   `.secrets/README.md`.
3. Nunca versione `.env`, `.secrets/`, dados pessoais ou dados reais de saúde.

Os segredos são montados em `/run/secrets/`, não são variáveis de ambiente,
estão ignorados pelo Git e são excluídos do contexto de build pelo
`.dockerignore`.

## Executar o MVP

```powershell
docker compose config --quiet
docker compose up --build --wait
docker compose ps
```

A aplicação fica disponível somente no host local:

- interface: `http://localhost:5000`;
- healthcheck: `http://localhost:5000/health`.

Executar a suíte principal e encerrar:

```powershell
docker compose --profile test run --rm cardioia-test
docker compose down
```

## IBM Watson Assistant

O arquivo `.env` seleciona a API com `WATSON_API_PROFILE=v2` ou `v1`. Para v2,
preencha URL, versão e environment/assistant ID; para v1, preencha URL, versão e
workspace ID. Grave a chave apenas em `.secrets/watson_api_key` e altere
`ASSISTANT_MODE=watson`.

Um arquivo de credenciais IBM no formato `ASSISTANT_URL`/
`ASSISTANT_IAM_APIKEY` pode ser importado sem imprimir os valores:

```powershell
.\scripts\import_ibm_credentials.ps1 -CredentialsPath 'C:\caminho\ibm-credentials.env'
docker compose run --rm --entrypoint python cardioia-app watson/import_workspace.py
docker compose --profile test run --rm --entrypoint python cardioia-test tests/watson_live_test.py
```

A modelagem importável e o roteiro de validação estão em `watson/`. A integração
real v1 foi aprovada em 24/08/2026; o modo mock continua disponível para execução
offline sem credencial.

## Ir Além 1 — Gemini

Executar os testes determinísticos e a extração real:

```powershell
docker compose --profile genai run --rm genai-test
docker compose --profile genai-live run --rm genai-live
```

O perfil live usa `gemini-3.5-flash-lite`, lê
`.secrets/gemini_api_key` como Docker secret e envia somente o exemplo fictício.
A saída estruturada não dispara nenhuma ação externa.

## Ir Além 2 — RPA híbrido

```powershell
docker compose --profile rpa up --build --abort-on-container-exit --exit-code-from rpa-test
docker compose --profile rpa down
```

O PostgreSQL contém leituras sintéticas; o MongoDB registra execuções, eventos
e mensagens. O worker executa dois ciclos, usa menor privilégio, evita
duplicidade e marca toda ação para revisão humana. Os bancos não publicam
portas no host.

## Gerar o vídeo demonstrativo

Com os frames reais da interface disponíveis em `output/video/frames/`, gere as
telas inicial/final, normalize as capturas e renderize o MP4 inteiramente em
Docker:

```powershell
docker compose --profile video run --build --rm video-assets
docker compose --profile video run --build --rm video-render
```

O resultado fica em `output/video/cardioia-demonstracao.mp4`. O vídeo não
contém áudio, credenciais ou dados pessoais; usa somente mensagens fictícias.

## Endpoints

- `GET /` — interface web;
- `GET /health` — saúde local do processo;
- `POST /api/chat` — envia uma mensagem ao adapter configurado;
- `DELETE /api/conversations/{conversation_id}` — encerra o contexto temporário.

## Estrutura

```text
backend/       aplicação Flask, adapters e interface
genai/         extração estruturada Gemini e referência offline
rpa/           worker, modelos didáticos e inicialização dos bancos
tests/         testes do MVP e adapters
watson/        exportação e documentação conversacional
docs/          arquitetura, relatórios, evidências e entrega
compose.yaml   orquestração oficial de todos os perfis
```

## Limitações

- conversas do MVP ficam em memória e são perdidas ao recriar o contêiner;
- a aplicação é acadêmica e local, não preparada para exposição pública;
- saídas de Watson, Gemini e do classificador didático exigem revisão humana.
