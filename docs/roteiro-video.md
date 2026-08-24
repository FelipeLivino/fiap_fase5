# Roteiro do vídeo - máximo 3 minutos

Tempo-alvo: 2min40s. Não mostrar `.env`, `.secrets`, `docker inspect` ou chaves.

| Tempo | Cena | Narração sugerida |
|---:|---|---|
| 0:00-0:15 | Título e estrutura do projeto | “Este é o CardioIA, protótipo acadêmico executado integralmente em Docker.” |
| 0:15-0:35 | `docker compose up --build --wait` e `docker compose ps` | Mostrar o serviço saudável e a porta somente local. |
| 0:35-1:05 | Interface e saudação | Destacar aviso de dados fictícios, limites e resposta do Watson. |
| 1:05-1:35 | Relato fictício + confirmação | Demonstrar contexto sem apresentar diagnóstico. |
| 1:35-1:55 | Fallback | Enviar frase fora do escopo e mostrar recuperação. |
| 1:55-2:10 | Segurança | Usar frase fictícia de urgência e mostrar orientação fixa ao SAMU 192. |
| 2:10-2:30 | Testes Docker | Mostrar a suíte principal aprovada; não abrir logs com dados de entrada. |
| 2:30-2:40 | Encerramento | Apontar export Watson, relatório e limitações. |

Antes de gravar, trocar `ASSISTANT_MODE=watson`, confirmar que a badge mostra
`watson` e executar os casos reais. Se a integração não estiver comprovada, não
afirmar no vídeo que a resposta veio do Watson.
