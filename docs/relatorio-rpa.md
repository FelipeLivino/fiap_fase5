# Relatório técnico - Ir Além 2

## Objetivo e limites

A automação processa somente leituras e mensagens fictícias. O resultado
`alerta_simulado` é um evento acadêmico: não contata pessoas, não altera
tratamento e exige revisão humana.

## Arquitetura

O perfil Docker `rpa` contém PostgreSQL para leituras estruturadas, MongoDB para
mensagens/eventos/auditoria e um worker Python. Nenhum banco publica porta no
host. Healthchecks e `depends_on` impedem o worker de iniciar antes da prontidão.

O PostgreSQL usa `cardioia_rpa` apenas com `SELECT` e `UPDATE` na tabela de
leituras. O MongoDB usa uma role customizada limitada às três coleções do fluxo.
Senhas são montadas por Compose secrets.

## Técnica de IA

As leituras passam por detecção estatística de anomalias por z-score, cuja base
é uma amostra sintética fixa e versionada. Mensagens passam por um classificador
Multinomial Naive Bayes treinado com frases fictícias. Regras complementares
registram adesão fictícia não confirmada. Essas técnicas não são modelos
clínicos, não foram validadas para saúde e servem apenas à demonstração.

## Rastreabilidade e retomada

Cada ciclo recebe `execucao_id`. Cada fonte gera `fonte_chave` única combinando
tipo, ID e versão do modelo. Se o evento já tiver sido gravado, a restrição única
impede duplicação e a retomada pode marcar a origem como processada. Erros são
registrados somente pelo nome técnico da exceção, sem texto da mensagem.

## Executar

```powershell
docker compose --profile rpa up --build --abort-on-container-exit --exit-code-from rpa-test rpa-test
```

O teste exige dois ciclos, eventos normais e de alerta, mensagem interpretada,
ausência de duplicação, rejeição de acesso anônimo/senha incorreta e bloqueio de
tentativas administrativas pelo usuário do worker.
