# Migração do CardioIA para Watson Actions

Destino: assistente `Fiapinho`, ambiente de rascunho. O conteúdo usa somente
cenários fictícios e não executa diagnóstico, prescrição ou ação externa.

## Importação inicial

No editor **Actions**, use o botão **Upload intents** da barra da lista de ações
e envie `watson/actions-intents.csv`. O arquivo não possui cabeçalho; cada linha
segue o formato CSV `frase,intent`. Essa é a alternativa manual. A migração
executada usa `export_v2_skills.py`, `build_v2_actions_payload.py` e
`import_v2_actions.py` para preservar os comportamentos do sistema e criar as
sete ações com suas respostas.

## Ações e respostas

| Ação | Primeira resposta | Continuação |
|---|---|---|
| `saudacao` | Olá! Posso organizar um relato inicial fictício, explicar os limites do protótipo ou encerrar a conversa. O que deseja simular? | Encerrar a ação após a resposta. |
| `ajuda` | Descreva um cenário fictício com o que foi sentido, há quanto tempo e a intensidade. Eu apenas organizarei o relato; não farei avaliação médica. | Encerrar a ação após a resposta. |
| `relatar_sintoma` | Entendi o relato fictício. Informe, se souber, há quanto tempo ocorreu e como você descreveria a intensidade. Depois confirme se o registro está correto. | Coletar texto livre fictício; em seguida perguntar se o registro está correto. Se sim, responder com a confirmação. Se não, solicitar correção. |
| `confirmar` | Registro fictício confirmado. Ele serve apenas para demonstrar organização conversacional e não constitui avaliação médica. | Encerrar a ação após a resposta. |
| `negar` | Sem problema. Escreva novamente apenas a informação fictícia que deseja registrar. | Encerrar a ação após a resposta. |
| `encerrar` | Conversa encerrada. Este protótipo não substitui orientação profissional. Em urgência no Brasil, procure um serviço de emergência ou ligue 192. | Encerrar a ação após a resposta. |
| `sinal_urgencia` | Isso pode representar uma urgência. No Brasil, ligue agora para o SAMU 192 ou procure imediatamente um serviço de emergência. Não espere uma resposta deste protótipo. | Encerrar a ação imediatamente. Não coletar dados nem chamar extensão. |

## Comportamento geral

- Saudação inicial: `Olá! Sou o CardioIA, um protótipo acadêmico. Use apenas
  informações fictícias. Não faço diagnóstico nem prescrição. Como posso
  ajudar no cenário simulado?`
- `No action matches`: `Não consegui relacionar a mensagem ao fluxo acadêmico.
  Tente escrever “ajuda”, relatar um cenário fictício ou digitar “encerrar”.`
- A ação `sinal_urgencia` deve permanecer independente e sem qualquer chamada
  externa, diagnóstico ou interpretação clínica.
- Desabilitar respostas generativas para as mensagens clínicas deste protótipo;
  as respostas avaliadas devem continuar determinísticas.
- Não adicionar custom extensions, webhooks, live agent ou coleta de dados
  pessoais nesta fase.

## Validação após a migração

1. Obter o Assistant ID ou Environment ID em **Assistant settings > Assistant
   IDs and API details**.
2. Configurar localmente `WATSON_API_PROFILE=v2` e o identificador, sem
   versioná-lo.
3. Executar os casos W-01 a W-09 de `watson/registro-testes.md` pelo Docker.
4. Confirmar que W-07 recebe a resposta fixa do SAMU 192 e que W-08/W-09 usam
   o fallback, sem resposta generativa.
