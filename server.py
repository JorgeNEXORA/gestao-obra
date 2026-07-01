"""
PROARKH — Gestão de Obra
Servidor FastAPI + SQLite.

Cada obra é guardada como um documento JSON numa tabela SQLite. Isto dá
isolamento por obra (dois dispositivos a editar obras diferentes não colidem)
e mantém o modelo de dados simples e evolutível.

Arranque:
    pip install -r requirements.txt
    python server.py
    -> http://localhost:8765
"""

import json
import os
import sqlite3
import time
from contextlib import closing

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("GO_DB_PATH", os.path.join(BASE, "gestao_obra.db"))
INDEX = os.path.join(BASE, "index.html")
PORT = int(os.environ.get("PORT", "8765"))


# ---------------------------------------------------------------- base de dados
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(db()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS obras(
                id         TEXT PRIMARY KEY,
                nome       TEXT,
                cliente    TEXT,
                updated_at REAL,
                doc        TEXT NOT NULL
            )"""
        )
        conn.commit()
        n = conn.execute("SELECT COUNT(*) AS c FROM obras").fetchone()["c"]
        if n == 0:
            _seed(conn)


def _uid():
    return format(int(time.time() * 1000), "x") + os.urandom(2).hex()


def _seed(conn):
    """Cria uma obra de demonstração no primeiro arranque."""
    c1, c2 = _uid(), _uid()
    obra = {
        "id": _uid(),
        "nome": "Moradia Vila Cova",
        "cliente": "João Silva",
        "codigo": "CLI-26-001",
        "morada": "Barcelos",
        "dataInicio": "2026-04-10",
        "prazoDias": 180,
        "capitulos": [
            {"id": c1, "nome": "1 · Movimento de Terras", "artigos": [
                {"id": _uid(), "codigo": "1.1", "designacao": "Escavação em terreno de qualquer natureza", "unidade": "m³", "qtd": 120, "preco": 8.5},
                {"id": _uid(), "codigo": "1.2", "designacao": "Aterro compactado", "unidade": "m³", "qtd": 60, "preco": 6.0},
            ]},
            {"id": c2, "nome": "2 · Estrutura", "artigos": [
                {"id": _uid(), "codigo": "2.1", "designacao": "Betão armado em fundações C25/30", "unidade": "m³", "qtd": 45, "preco": 145},
                {"id": _uid(), "codigo": "2.2", "designacao": "Laje maciça e=0.20m", "unidade": "m²", "qtd": 210, "preco": 62},
                {"id": _uid(), "codigo": "2.3", "designacao": "Pilares e vigas", "unidade": "m³", "qtd": 28, "preco": 180},
            ]},
        ],
        "autos": [],
        "custos": [
            {"id": _uid(), "data": "2026-04-22", "capituloId": c1, "descricao": "Aluguer retroescavadora", "fornecedor": "Terraplanagens Lda", "valor": 1450},
        ],
        "tarefas": [
            {"id": _uid(), "titulo": "Confirmar armaduras com fornecedor", "responsavel": "Jorge", "prazo": "2026-07-10", "prioridade": "alta", "estado": "pendente"},
            {"id": _uid(), "titulo": "Marcar visita de fiscalização", "responsavel": "Jorge", "prazo": "2026-07-05", "prioridade": "media", "estado": "pendente"},
        ],
    }
    _upsert(conn, obra)
    conn.commit()


def _upsert(conn, obra):
    conn.execute(
        "INSERT INTO obras(id,nome,cliente,updated_at,doc) VALUES(?,?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET nome=excluded.nome, cliente=excluded.cliente, "
        "updated_at=excluded.updated_at, doc=excluded.doc",
        (obra["id"], obra.get("nome", ""), obra.get("cliente", ""), time.time(), json.dumps(obra, ensure_ascii=False)),
    )


# ------------------------------------------------------------------------- app
app = FastAPI(title="PROARKH — Gestão de Obra", version="1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/obras")
def list_obras():
    with closing(db()) as conn:
        rows = conn.execute("SELECT doc FROM obras ORDER BY nome").fetchall()
        return [json.loads(r["doc"]) for r in rows]


@app.get("/api/obras/{obra_id}")
def get_obra(obra_id: str):
    with closing(db()) as conn:
        row = conn.execute("SELECT doc FROM obras WHERE id=?", (obra_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Obra não encontrada")
        return json.loads(row["doc"])


@app.put("/api/obras/{obra_id}")
def put_obra(obra_id: str, obra: dict = Body(...)):
    obra["id"] = obra_id
    with closing(db()) as conn:
        _upsert(conn, obra)
        conn.commit()
    return {"ok": True, "id": obra_id, "updated_at": time.time()}


@app.delete("/api/obras/{obra_id}")
def delete_obra(obra_id: str):
    with closing(db()) as conn:
        conn.execute("DELETE FROM obras WHERE id=?", (obra_id,))
        conn.commit()
    return {"ok": True}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return FileResponse(INDEX)


if __name__ == "__main__":
    init_db()
    print(f"PROARKH — Gestão de Obra  ·  http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
