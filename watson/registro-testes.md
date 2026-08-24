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

O primeiro reteste revelou confusão entre ajuda/relato e encerramento/confirmação.
Foram adicionados exemplos semanticamente próximos — sem copiar as frases de
validação —, o workspace foi atualizado e todos os nove casos passaram.
