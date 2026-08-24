# Decisões da Fase 0

Data da validação: 24/08/2026.

## Ambiente confirmado

- Docker Desktop 4.84.0;
- Docker Engine 29.6.2 em modo `linux/amd64`;
- Docker Compose 5.3.1;
- nenhuma aplicação CardioIA em execução antes do primeiro build.

## Decisões do MVP

- Docker Compose é o único caminho oficial de execução e demonstração.
- O MVP usa um contêiner `cardioia-app`, sem banco de dados e sem volume de conversa.
- A interface é servida pelo Flask na mesma origem da API.
- A porta padrão é publicada somente em `127.0.0.1:5000`.
- O estado da conversa é efêmero, em memória, com TTL de 900 segundos.
- O healthcheck verifica somente `/health`, sem chamar o Watson.
- Dados e exemplos são exclusivamente fictícios.
- O modo `mock` existe somente para validar a fundação das Fases 0 e 1.

## Decisões concluídas nas fases seguintes

- o runtime final usa Assistant v2 stateful, mantendo workspace v1 como rollback;
- a instância acadêmica foi configurada por Docker secret;
- sete Actions, 46 exemplos e três entidades foram migrados para o `Fiapinho`;
- o serviço mock foi substituído pela integração real v2 na validação final.

## Evidências da primeira execução

Em 24/08/2026, neste ambiente de referência:

- `docker compose config --quiet` terminou com código 0;
- `docker compose build --no-cache` produziu a imagem local `cardioia-mvp:local`;
- `docker compose up --wait` iniciou o serviço e atingiu o estado `healthy`;
- `GET /health` retornou `status=ok`;
- o runner `cardioia-test` passou em nove verificações HTTP;
- o processo da aplicação executou com UID `10001`, sem privilégios de `root`;
- a porta foi publicada somente em `127.0.0.1:5000`.

Essas evidências encerram a fundação técnica desta máquina, mas não substituem os
portões pendentes da Fase 0: segunda máquina, equipe e revisão do conteúdo
didático autorizado. O portão Watson real foi concluído com Actions v2.
