# Contrato de integração - Ir Além 1

O módulo `genai.extractor` é chamável pelo backend sem alterar o MVP. A entrada é
um texto fictício de até 5.000 caracteres. A saída segue `ExtracaoClinica` e
sempre contém `status`, `sintomas`, `medidas`, `medicamentos_mencionados`,
`campos_ausentes`, `inconsistencias`, `trechos_fonte` e `observacao`.

O modo `deterministic` serve apenas como referência repetível de teste. O modo
`gemini` é a implementação generativa e usa saída estruturada por JSON Schema.
Nenhum resultado dispara contato, tratamento ou alerta externo.

```powershell
docker compose --profile genai run --rm genai-test
docker compose --profile genai-live run --rm genai-live
```

O perfil live usa `gemini-3.5-flash-lite`. A chave deve existir localmente em
`GEMINI_API_KEY` no `.env`; nunca deve entrar no repositório, na imagem ou no
comando. O Compose a injeta apenas no contêiner `genai-live`. O arquivo de
entrada contém apenas dados fictícios. A chamada real foi validada em Docker em
24/08/2026.
