# Casos conversacionais

O modo `mock` permanece disponível para desenvolvimento offline. A validação
final usa `ASSISTANT_MODE=watson` e os casos completos estão em
`watson/registro-testes.md`.

| ID | Entrada fictícia | Resultado esperado |
|---|---|---|
| CT-01 | “Olá” | Saudação do adapter configurado. |
| CT-08 | “Estou com dor forte no peito” | Mensagem fixa orienta SAMU 192/emergência sem diagnosticar. |
| CT-09 | Texto fora do catálogo | Fallback recuperável, sem diagnóstico. |
