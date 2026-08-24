# Matriz de testes executada

Data local: 24/08/2026.

| Grupo | Cobertura | Resultado local |
|---|---|---|
| MVP HTTP | `/health`, `/`, validação, chat, contexto, segurança, delete/410 | 9 aprovados |
| Backend/Watson | adapters v1/v2, múltiplas mensagens, sessão, contexto, resposta vazia, export | 13 aprovados |
| Ir Além 1 | schema, ausências, ambiguidade, contradição, injection, entrada inválida | 12 aprovados |
| Ir Além 2 | dois ciclos, idempotência, alerta, texto, autenticação e menor privilégio | 13 aprovados |
| Compose | configuração resolvida sem impressão | Aprovado |
| Estabilidade | build sem cache e três inicializações consecutivas com `--wait` | Aprovado |
| Contêiner MVP | healthcheck, UID 10001, bind 127.0.0.1 | Aprovado |
| Dependências | `pip check` nas imagens MVP, GenAI e RPA | Aprovado |
| Watson real | importação, treinamento e 9 frases inéditas pelo backend Docker | 9 aprovados |
| Gemini real | extração estruturada com `gemini-3.5-flash-lite` pelo `genai-live` | Aprovado |
| Segunda máquina | build sem cache e execução | Pendente de integrante |

Os totais representam asserções automatizadas, não alegações de validação
clínica. Os testes RPA usam somente volumes e registros fictícios.
