# Governança da Fase 0

## Escopo congelado

O CardioIA organiza um atendimento inicial fictício em linguagem natural. Ele
não diagnostica, não prescreve, não substitui profissional de saúde e não deve
receber dados reais.

| Camada | Situação | Dependência externa |
|---|---|---|
| MVP Watson + Flask + interface | Concluído localmente | Nenhuma; Watson real validado |
| Ir Além 1 - Gemini | Concluído localmente | Nenhuma; chamada real validada em Docker |
| Ir Além 2 - RPA e dados híbridos | Em execução | Nenhuma; stack local Docker |

## Fluxos da demonstração

1. saudação e apresentação dos limites;
2. relato fictício, complemento e confirmação;
3. fallback recuperável;
4. mensagem de segurança com orientação fixa ao SAMU 192/emergência;
5. encerramento explícito.

## Responsabilidades

Os nomes devem ser preenchidos pela equipe antes da entrega. Não foram
inventados durante a implementação.

| Papel | Responsável | Revisor |
|---|---|---|
| Watson e conteúdo conversacional | A definir | A definir |
| Backend e integrações | A definir | A definir |
| Interface e acessibilidade | A definir | A definir |
| Docker, QA e documentação | A definir | A definir |
| Ir Além 1 e 2 | A definir | A definir |

## Convenções

- branches curtas por fase e revisão por outro integrante;
- commits descritivos, sem segredos, dados reais ou artefatos temporários;
- toda execução oficial ocorre via Docker Compose;
- evidências registram comando, data, resultado e limitação;
- qualquer texto informativo clínico exige fonte e revisão humana antes do uso.

## Portões externos

- confirmar as tecnologias efetivamente mostradas no material didático;
- atribuir os integrantes e revisores;
- testar o projeto em uma segunda máquina;
- criar o repositório público e gravar o vídeo final.
