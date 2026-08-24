# IBM Watson Assistant

Artefatos da Fase 2 do CardioIA. Nenhum arquivo desta pasta contém credenciais,
IDs de instância ou dados reais.

## Conteúdo

- `assistant-export.json`: workspace clássico Watson Assistant v1, adequado para
  importação e também como especificação versionada do fluxo;
- `fluxo-conversacional.md`: catálogo, prioridade dos nós e variáveis de contexto;
- `registro-testes.md`: casos e resultados da validação real.
- `import_workspace.py`: importação/atualização idempotente do workspace v1.
- `actions-intents.csv`: frases de treino no formato de migração
  intents→Actions aceito pela interface IBM;
- `actions-migration.md`: mapa das sete ações, respostas, fallback e validação
  do runtime v2.
- `export_v2_skills.py`: backup do conteúdo atual do rascunho;
- `build_v2_actions_payload.py`: geração determinística do payload com Actions;
- `import_v2_actions.py`: importação assíncrona e acompanhamento do treinamento.

## Importar e conectar

1. Importe `assistant-export.json` em uma skill de diálogo clássica ou execute
   `watson/import_workspace.py` pelo contêiner.
2. Teste os casos de `registro-testes.md` na plataforma.
3. Para runtime v2, associe a skill a um assistant/environment e configure
   `WATSON_API_PROFILE=v2`, `WATSON_ASSISTANT_ID` e `WATSON_ENVIRONMENT_ID`.
4. Para o workspace clássico usado diretamente, configure
   `WATSON_API_PROFILE=v1` e `WATSON_WORKSPACE_ID`.
5. Coloque a chave somente em `.secrets/watson_api_key` e altere
   `ASSISTANT_MODE=watson`.

Em 24/08/2026, o workspace v1 foi preservado e sua modelagem foi migrada para
sete Actions no assistente `Fiapinho`, plano Lite. A interface registrou sete
ações sem erros, com 46 exemplos; o runtime v2 foi aprovado nos nove casos
reais. IDs e credenciais permanecem somente nos arquivos locais ignorados pelo
Git.
