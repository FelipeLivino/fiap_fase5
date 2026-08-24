# Relatório - IA Generativa e extração estruturada

## Finalidade

O Ir Além 1 transforma texto clínico fictício não estruturado em JSON. Extração
é diferente de interpretação: o módulo copia fatos explícitos, mas não conclui
diagnóstico, tratamento, urgência ou risco. Toda saída informa que o cenário é
fictício e exige revisão humana antes de qualquer uso posterior.

## Prompt e esquema

O prompt define papel, objetivo, limites, fonte autorizada e formato obrigatório.
O conteúdo é delimitado por `<entrada_ficticia>` e tratado como dado não
confiável. Ordens incluídas nesse bloco não podem alterar as regras. Informação
ausente usa `null` ou lista vazia; ambiguidades, contradições, unidade ausente e
tentativa de prompt injection geram `status=needs_review`.

O schema Pydantic proíbe campos extras e contém sintomas, medidas,
medicamentos mencionados, ausências, inconsistências e trechos-fonte. A API
Gemini recebe o JSON Schema no modo de saída estruturada. Depois da geração, uma
segunda validação local confirma tipos, remove citações que não sejam substrings
da entrada, fixa a observação ética e força revisão quando identifica instrução
embutida.

## Implementação

`GeminiExtractor` usa o SDK oficial `google-genai`, o modelo estável
`gemini-3.5-flash-lite` e lê a chave do Google AI Studio em
`/run/secrets/gemini_api_key`. O modo `DeterministicExtractor` é uma
referência offline para testes repetíveis e não é apresentado como IA
generativa. Ambos implementam o mesmo contrato, permitindo comparar o schema e
as guardrails sem gastar quota.

O perfil `genai` executa doze verificações: caso completo, campos ausentes,
unidade ambígua, valores contraditórios, instrução maliciosa e entrada vazia. O
perfil `genai-live` envia apenas o exemplo fictício ao Gemini. A saída não aciona
automaticamente outro serviço.

## Limitações e ética

Em 24/08/2026, a execução real pelo perfil `genai-live` processou o exemplo
fictício, retornou JSON válido segundo o schema e preservou os dois
trechos-fonte esperados. A chave ficou apenas no secret local ignorado pelo Git
e excluído do contexto de build.

Modelos generativos são probabilísticos e podem omitir ou alterar informações
mesmo com schema. JSON válido não significa conteúdo correto. Os exemplos não
contêm dados reais e a chave não entra na imagem. O módulo não aceita imagem
nesta versão porque o enunciado permite texto ou imagem e o fluxo textual é
mais simples de auditar.

Referências técnicas: documentação oficial do Google para autenticação da API
Gemini e Structured Outputs.
