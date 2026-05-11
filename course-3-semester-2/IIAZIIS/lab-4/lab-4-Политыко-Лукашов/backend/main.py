import logging

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import syntax, help as help_route
from core.models import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
init_db()

app = FastAPI(
    title="Семантико-синтаксический анализатор",
    description="Семантико-синтаксический анализ русского текста, форматы TXT, RTF, DOCX",
    version="4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(syntax.router, prefix="/api", tags=["Синтаксис"])
app.include_router(help_route.router, prefix="/api", tags=["Справка"])


@app.get("/")
def root():
    return {
        "message": "Семантико-синтаксический анализатор работает",
        "docs": "/docs",
        "subject": "Семантико-синтаксический анализ (русский, DOCX)"
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "semantics-syntax-analyzer", "version": "4.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
