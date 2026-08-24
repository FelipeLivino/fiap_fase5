# Evidências da validação local

Data: 24/08/2026. Ambiente: Docker Desktop/Engine e Docker Compose no Windows.
As evidências não substituem o teste obrigatório por outro integrante em uma
segunda máquina.

## MVP e Docker

- `docker compose config --quiet`: aprovado;
- `docker compose build --no-cache cardioia-app`: aprovado;
- três sequências independentes de `docker compose down` seguidas de
  `docker compose up --build --wait`: todas chegaram a `healthy`;
- suíte conteinerizada: 13 verificações unitárias e 9 smoke tests aprovados;
- porta do MVP publicada somente em `127.0.0.1:5000`;
- imagens MVP, GenAI e RPA executam como UID 10001;
- `pip check` nas três imagens: nenhuma dependência quebrada.

## IBM Watson Assistant

- credenciais importadas de arquivo externo sem impressão dos valores;
- workspace v1 criado, treinado e atualizado de forma idempotente;
- suíte HTTP principal aprovada no modo Watson real;
- nove frases inéditas aprovadas, incluindo segurança e fallback;
- chave, URL completa e workspace ID permanecem fora dos arquivos versionados.

## Ir Além 1

- 12 verificações offline aprovadas;
- chamada real ao `gemini-3.5-flash-lite` aprovada pelo perfil `genai-live`;
- resposta validada pelo schema Pydantic e guardrails locais;
- segredo ignorado pelo Git, ausente do contexto de build e ausente das
  variáveis persistidas nas imagens.

## Ir Além 2

- PostgreSQL e MongoDB ficaram `healthy` sem portas publicadas no host;
- worker completou dois ciclos com `execucao_id` distintos;
- nova execução não duplicou as fontes já processadas;
- 13 verificações de fluxo, idempotência, autenticação e menor privilégio
  aprovadas.

## PDF

- três relatórios A4 gerados em `output/pdf/`;
- cada relatório possui uma página;
- texto extraível e inspeção visual sem corte, sobreposição ou página vazia.

## Vídeo demonstrativo

- frames reais capturados da interface executada em Docker no modo Watson;
- mensagens exclusivamente fictícias, incluindo saudação, relato, urgência e
  fallback;
- telas inicial e final e normalização dos frames geradas pelo perfil Docker
  `video`;
- MP4 renderizado pelo FFmpeg em contêiner: H.264, 1280 × 720, 30 fps e
  aproximadamente 46 segundos;
- quadros extraídos do próprio MP4 e revisados visualmente.

## Pendências externas

- preencher integrantes e revisores;
- repetir o build em uma segunda máquina;
- revisar o vídeo e comparar a entrega com o material didático em equipe.
