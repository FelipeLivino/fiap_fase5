# Casos de integração

| ID | Procedimento | Resultado esperado |
|---|---|---|
| CT-D01 | `docker compose build --no-cache` | Imagem construída com sucesso. |
| CT-D02 | `docker compose up --wait` | Serviço fica `healthy`. |
| CT-D03 | Abrir `http://localhost:5000/health` e `/` | API e interface respondem. |
| CT-D06 | Verificar UID e artefatos da imagem | Processo não-root; segredos fora da imagem. |
| CT-D08 | `docker compose --profile test run --rm cardioia-test` | Smoke tests terminam com sucesso. |
