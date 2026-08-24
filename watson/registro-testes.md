# Registro de testes do Watson

Os resultados abaixo foram executados contra a instância acadêmica real pelo
backend conteinerizado em 24/08/2026. As frases de validação são diferentes dos
exemplos de treino.

| ID | Frase inédita fictícia | Esperado | Especificação | Watson real |
|---|---|---|---|---|
| W-01 | “Boa tarde, quero começar” | `saudacao` | Aprovado | Aprovado |
| W-02 | “Que tipo de simulação você aceita?” | `ajuda` | Aprovado | Aprovado |
| W-03 | “No exemplo meu coração ficou acelerado por dez minutos” | `relatar_sintoma` + entities | Aprovado | Aprovado |
| W-04 | “Sim, o registro está certo” | `confirmar` | Aprovado | Aprovado |
| W-05 | “Quero alterar o que escrevi” | `negar` | Aprovado | Aprovado |
| W-06 | “Até mais, pode finalizar” | `encerrar` | Aprovado | Aprovado |
| W-07 | “Dor muito forte no peito e suor frio” | `sinal_urgencia` | Aprovado | Aprovado |
| W-08 | “Fale sobre astronomia” | fallback | Aprovado | Aprovado |
| W-09 | “Qual medicamento devo tomar?” | fallback/limite | Aprovado | Aprovado |

O primeiro reteste do workspace clássico revelou confusão entre ajuda/relato e
encerramento/confirmação. Na migração para Actions v2, W-01 também foi inicialmente
classificado como encerramento durante o treinamento. Foram adicionados três
exemplos semanticamente próximos de saudação — sem copiar a frase de validação —
e, após a propagação do modelo, todos os nove casos passaram no `Fiapinho` v2.
