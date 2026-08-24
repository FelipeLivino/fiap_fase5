# CardioIA - Relatório do fluxo conversacional

## Objetivo

O CardioIA é um protótipo acadêmico de atendimento inicial conversacional para
cenários cardiológicos fictícios. Ele recebe mensagens em linguagem natural,
organiza o relato e devolve respostas contextualizadas. O sistema não realiza
diagnóstico, não prescreve medicamentos, não calcula risco e não substitui um
profissional ou serviço de emergência. A interface também orienta o usuário a
não inserir dados pessoais ou informações reais de saúde.

## Fluxo no Watson Assistant

A skill possui sete intents: `saudacao`, `ajuda`, `relatar_sintoma`,
`confirmar`, `negar`, `encerrar` e `sinal_urgencia`. As entities `sintoma`,
`duracao` e `intensidade` reconhecem somente elementos expressos pelo usuário.
Elas não convertem termos em conclusão médica.

Os dialog nodes são avaliados por prioridade. O nó de segurança precede os
fluxos comuns e responde com texto fixo orientando SAMU 192 ou serviço de
emergência no Brasil. Saudação e ajuda apresentam as possibilidades; o relato
solicita duração e intensidade; confirmação/correção usam a variável de contexto
`em_confirmacao`; encerramento reforça os limites; e `anything_else` mantém a
conversa recuperável. A configuração versionada está em
`watson/assistant-export.json`.

## Integração e interface

O navegador chama apenas `POST /api/chat` no backend Flask. Cada conversa recebe
um UUID público imprevisível armazenado em `sessionStorage`. No perfil Watson v2,
o backend cria e mantém o session ID interno do provedor; no perfil clássico v1,
mantém o contexto devolvido pelo workspace. O identificador interno, a chave e a
URL privada nunca chegam ao frontend.

A API valida tipo de conteúdo, JSON, presença e tamanho da mensagem. Respostas
textuais do Watson são normalizadas em uma lista, preservando a ordem. Timeout,
falha de credencial, indisponibilidade e resposta vazia produzem HTTP 503 com
mensagem fixa e segura, sem stack trace. Logs registram apenas request ID, intent
e status, nunca o texto enviado.

A interface apresenta aviso ético, histórico visualmente separado, envio por
Enter ou botão, estado de carregamento, erro recuperável e nova conversa. Todo
texto retornado é inserido por `textContent`, evitando HTML fornecido pelo
provedor.

## Execução, qualidade e limitações

Docker Compose é o único caminho oficial. A imagem usa Python 3.12, processo
não-root, filesystem somente leitura, capabilities removidas, healthcheck local
e publicação exclusiva em `127.0.0.1:5000`. Segredos são montados em runtime e
ficam fora do build.

Testes conteinerizados cobrem saúde, interface, validação, continuidade,
encerramento, segurança, adapters Watson v1/v2 e exportação JSON. Os perfis
opcionais de IA generativa e RPA são independentes e não quebram o MVP.

O modo `mock` foi usado na fundação e permanece disponível para desenvolvimento
offline. Na validação final, a configuração versionada foi importada em um
workspace Watson v1, treinada e acessada pelo backend Docker. Nove frases
inéditas cobriram todos os intents e os fallbacks; depois de um ajuste de treino,
todos os casos passaram. O protótipo não possui validação clínica, persistência
de conversa, alta disponibilidade ou finalidade de produção.
