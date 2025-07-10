# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.api.routes import auth, analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisiert die Datenbankverbindung beim Start."""
    await init_db()
    yield
    print("API shutdown.")

app = FastAPI(
    title="Website Analyzer API",
    lifespan=lifespan
)

# Deine CORS-Einstellungen sind korrekt und bleiben unverändert.
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
    "http://127.0.0.1:5177",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# KORREKTUR: Wir entfernen die /api/v1-Präfixe, um den 404-Fehler zu beheben
# und deine ursprüngliche, einfache URL-Struktur beizubehalten.
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])

@app.get("/", tags=["Status"])
def read_root():
    """Ein einfacher Endpunkt, um zu prüfen, ob die API online ist."""
    return {"status": "ok", "message": "Welcome to the Website Analyzer API!"}