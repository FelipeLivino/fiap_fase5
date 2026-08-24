#!/usr/bin/env bash
set -Eeuo pipefail

rpa_password="$(< /run/secrets/rpa_postgres_password)"

psql --set ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set rpa_password="$rpa_password" <<'SQL'
CREATE ROLE cardioia_rpa LOGIN PASSWORD :'rpa_password';

CREATE TABLE leituras_simuladas (
    id BIGSERIAL PRIMARY KEY,
    paciente_simulado_id VARCHAR(32) NOT NULL,
    coletado_em TIMESTAMPTZ NOT NULL,
    pressao_sistolica INTEGER NOT NULL,
    pressao_diastolica INTEGER NOT NULL,
    frequencia_cardiaca INTEGER NOT NULL,
    adesao_tratamento VARCHAR(16) NOT NULL CHECK (adesao_tratamento IN ('sim', 'nao', 'desconhecida')),
    processado_em TIMESTAMPTZ NULL
);

INSERT INTO leituras_simuladas
    (paciente_simulado_id, coletado_em, pressao_sistolica,
     pressao_diastolica, frequencia_cardiaca, adesao_tratamento)
VALUES
    ('PAC-FICT-001', now() - interval '30 minutes', 120, 78, 72, 'sim'),
    ('PAC-FICT-002', now() - interval '20 minutes', 182, 112, 132, 'nao'),
    ('PAC-FICT-003', now() - interval '10 minutes', 114, 72, 68, 'sim');

GRANT CONNECT ON DATABASE cardioia TO cardioia_rpa;
GRANT USAGE ON SCHEMA public TO cardioia_rpa;
GRANT SELECT, UPDATE ON leituras_simuladas TO cardioia_rpa;
SQL
