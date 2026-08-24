# Arquitetura executada

```mermaid
flowchart LR
    UI[Navegador] -->|HTTP local| APP[cardioia-app\nFlask não-root]
    APP -->|v2 session ou v1 context| W[IBM Watson Assistant]
    G[genai-live\nperfil opcional] -->|JSON Schema| GEM[Gemini API]
    RW[rpa-worker\nperfil opcional] --> PG[(PostgreSQL\nsem porta no host)]
    RW --> MO[(MongoDB\nsem porta no host)]
```

- O MVP padrão sobe somente `cardioia-app`.
- Watson e Gemini são serviços externos; as chaves são Compose secrets.
- `genai` e `rpa` são perfis independentes.
- A rede `rpa-internal` é interna e não se conecta ao navegador.
- Volumes RPA persistem somente massa fictícia.
