const appDb = db.getSiblingDB("cardioia");
const workerPassword = fs
  .readFileSync("/run/secrets/rpa_mongo_password", "utf8")
  .trim();

appDb.createCollection("mensagens");
appDb.createCollection("eventos");
appDb.createCollection("execucoes");

appDb.mensagens.createIndex({ mensagem_id: 1 }, { unique: true });
appDb.eventos.createIndex({ fonte_chave: 1 }, { unique: true });
appDb.execucoes.createIndex({ execucao_id: 1 }, { unique: true });

appDb.createRole({
  role: "cardioiaRpaRole",
  privileges: [
    {
      resource: { db: "cardioia", collection: "mensagens" },
      actions: ["find", "update"],
    },
    {
      resource: { db: "cardioia", collection: "eventos" },
      actions: ["find", "insert", "update"],
    },
    {
      resource: { db: "cardioia", collection: "execucoes" },
      actions: ["find", "insert", "update"],
    },
  ],
  roles: [],
});

appDb.createUser({
  user: "cardioia_rpa",
  pwd: workerPassword,
  roles: [{ role: "cardioiaRpaRole", db: "cardioia" }],
});

appDb.mensagens.insertMany([
  {
    mensagem_id: "MSG-FICT-001",
    paciente_simulado_id: "PAC-FICT-001",
    criado_em: new Date(),
    texto_simulado: "Tomei a dose fictícia conforme combinado.",
    processado_em: null,
  },
  {
    mensagem_id: "MSG-FICT-002",
    paciente_simulado_id: "PAC-FICT-002",
    criado_em: new Date(),
    texto_simulado: "Esqueci uma dose no cenário de teste.",
    processado_em: null,
  },
]);
