from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json, os
from pathlib import Path

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

DB_FILE = Path("database.json")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD","blackhouse123")

def load_db():
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return []

def save_db(data):
    DB_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def logged(req: Request):
    return req.cookies.get("session") == ADMIN_PASSWORD

def require(req: Request):
    if not logged(req):
        raise RedirectResponse("/admin/login", 302)

@router.get("/login", response_class=HTMLResponse)
def login_page(req: Request):
    return templates.TemplateResponse("login.html", {"request": req})

@router.post("/login")
def login(req: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        resp = RedirectResponse("/admin/dashboard", 302)
        resp.set_cookie("session", ADMIN_PASSWORD)
        return resp
    return RedirectResponse("/admin/login", 302)

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(req: Request):
    require(req)
    banco = load_db()
    stats = {}
    for q in banco:
        t = q.get("topico", "Geral")
        stats[t] = stats.get(t, 0) + 1

    return templates.TemplateResponse("dashboard.html", {
        "request": req,
        "total": len(banco),
        "por_topico": stats
    })

@router.get("/questoes", response_class=HTMLResponse)
def lista(req: Request):
    require(req)
    banco = load_db()
    return templates.TemplateResponse("questions_list.html", {"request": req, "questoes": banco})

@router.get("/questoes/nova", response_class=HTMLResponse)
def nova(req: Request):
    require(req)
    return templates.TemplateResponse("question_form.html", {"request": req})

@router.post("/questoes/nova")
def criar(req: Request,
          pergunta: str = Form(...),
          opcoes: str = Form(...),
          correta: str = Form(...),
          comentario: str = Form(""),
          topico: str = Form("Geral")):

    require(req)
    banco = load_db()
    lista_opcoes = [x.strip() for x in opcoes.split("\n") if x.strip()]

    banco.append({
        "pergunta": pergunta,
        "opcoes": lista_opcoes,
        "correta": correta,
        "comentario": comentario,
        "topico": topico
    })

    save_db(banco)
    return RedirectResponse("/admin/questoes", 302)
