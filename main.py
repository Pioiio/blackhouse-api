from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from admin_panel import router as admin_router
import json
from pathlib import Path
import random

app = FastAPI(title="API Black House")

app.include_router(admin_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_FILE = Path("database.json")

def carregar_banco():
    if DB_FILE.exists():
        try:
            return json.loads(DB_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []

@app.get("/")
def root():
    return {"status": "API Black House ativa!"}

@app.get("/questoes")
def listar_questoes(qtd: int = 10, topico: str | None = None):
    banco = carregar_banco()

    if topico:
        filtradas = [q for q in banco if q.get("topico") == topico]
    else:
        filtradas = banco

    if not filtradas:
        return JSONResponse(
            {"erro": f"Não encontrei questões para o tópico '{topico}'."},
            status_code=404
        )

    random.shuffle(filtradas)
    return filtradas[:qtd]
