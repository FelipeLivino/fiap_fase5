# Segredos locais
Arquivos locais ignorados pelo Git e montados em `/run/secrets/` pelo Docker.

- `watson_api_key`: chave da instância IBM Watson Assistant;
- `gemini_api_key`: chave da API Gemini criada no Google AI Studio;
- os segredos do perfil RPA são placeholders fictícios de desenvolvimento e
  devem ser trocados antes de qualquer demonstração compartilhada.

Nunca cole uma chave em issue, commit, log, vídeo ou mensagem de chat.
Esta pasta não deve conter arquivos versionados além deste README.

- `watson_api_key` é montado pelo Docker Compose em `/run/secrets/watson_api_key`.
- Durante a Fase 1, o arquivo pode conter apenas o placeholder `mock-not-used`.
- Antes da integração real, substitua o placeholder pela chave acadêmica do Watson.
- Nunca mostre o conteúdo do arquivo em logs, capturas, vídeo ou comandos compartilhados.
