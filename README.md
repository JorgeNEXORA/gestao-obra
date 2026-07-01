# PROARKH — Gestão de Obra

Aplicação web para **orçamentação e gestão de obra**: orçamentos por capítulos e
artigos, autos de medição, controlo de custos (previsto vs. real) e gestão de
tarefas. Arquitetura cliente-servidor — acede-se de qualquer PC ou telemóvel
pelo browser, com os dados guardados num servidor central.

## Stack

- **Servidor:** Python + FastAPI
- **Base de dados:** SQLite (ficheiro único, zero configuração)
- **Frontend:** HTML/CSS/JS (sem dependências, um único ficheiro)

## Arranque rápido (Python)

```bash
pip install -r requirements.txt
python server.py
```

Abre **http://localhost:8765** no browser.

## Arranque com Docker (recomendado para servidor)

```bash
docker compose up -d
```

A base de dados fica em `./data/gestao_obra.db` (persiste entre atualizações).

## Acesso a partir de outros dispositivos

Com o servidor a correr numa máquina (PC do escritório, NAS ou VPS), abre nos
outros dispositivos:

```
http://<IP-do-servidor>:8765
```

Para acesso a partir de fora da rede local, expõe a porta 8765 através de uma
VPN, um túnel (ex: Cloudflare Tunnel) ou um proxy reverso com HTTPS.

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/obras` | Lista todas as obras |
| GET | `/api/obras/{id}` | Obtém uma obra |
| PUT | `/api/obras/{id}` | Cria/atualiza uma obra |
| DELETE | `/api/obras/{id}` | Elimina uma obra |
| GET | `/api/health` | Estado do servidor |

## Configuração

| Variável | Predefinição | Descrição |
|----------|--------------|-----------|
| `PORT` | `8765` | Porta do servidor |
| `GO_DB_PATH` | `./gestao_obra.db` | Caminho da base de dados |

## Estado

Protótipo funcional (v1.0). Próximos passos previstos: capítulos padrão
A01–A27, margem por artigo, resumo com custos indiretos/garantia/lucro,
composições de preços e contas de utilizador.

## Licença

A definir antes da publicação.
