# IBM Watson Assistant

Artefatos da Fase 2 do CardioIA. Nenhum arquivo desta pasta contém credenciais,
IDs de instância ou dados reais.

## Conteúdo

- `assistant-export.json`: workspace clássico Watson Assistant v1, adequado para
  importação e também como especificação versionada do fluxo;
- `fluxo-conversacional.md`: catálogo, prioridade dos nós e variáveis de contexto;
- `registro-testes.md`: casos e resultados da validação real.
- `import_workspace.py`: importação/atualização idempotente do workspace v1.

## Importar e conectar

1. Importe `assistant-export.json` em uma skill de diálogo clássica ou execute
   `watson/import_workspace.py` pelo contêiner.
2. Teste os casos de `registro-testes.md` na plataforma.
3. Para runtime v2, associe a skill a um assistant/environment e configure
   `WATSON_API_PROFILE=v2` e `WATSON_ASSISTANT_ID`.
4. Para o workspace clássico usado diretamente, configure
   `WATSON_API_PROFILE=v1` e `WATSON_WORKSPACE_ID`.
5. Coloque a chave somente em `.secrets/watson_api_key` e altere
   `ASSISTANT_MODE=watson`.

Em 24/08/2026, a configuração versionada foi importada em um workspace v1 de
plano Lite, treinada e aprovada nos nove casos reais. IDs e credenciais
permanecem somente nos arquivos locais ignorados pelo Git.
