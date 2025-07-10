# app/db/database.py

import motor.motor_asyncio
from beanie import init_beanie
from app.core.config import settings
from app.db.models import User, AnalysisJob # Importiert unsere Modelle
import asyncio

# Wir entfernen die globale Client-Variable, da sie die Ursache des Problems ist.

async def init_db():
    """
    Initialisiert die Datenbankverbindung und Beanie.
    Diese Funktion wird jetzt von beiden, API und Worker, aufgerufen und ist robust gegen geschlossene Event-Loops.
    """
    print("--- DB: Initialisiere Datenbankverbindung... ---")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Verbindungsstring erstellen, genau wie in deinem Code
            mongo_uri = f"mongodb://{settings.MONGO_INITDB_ROOT_USERNAME}:{settings.MONGO_INITDB_ROOT_PASSWORD}@{settings.MONGO_HOST}:27017"
            
            # Client erstellen. Dies geschieht jetzt bei jedem Aufruf von init_db,
            # was den Fehler "Event loop is closed" verhindert.
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            
            # Verbindung pingen
            await client.admin.command('ping') 
            
            # Beanie mit allen Dokumenten initialisieren, genau wie in deinem Code.
            # Annahme: Der DB-Name in deiner .env ist 'website_analyzer_db' oder du passt es hier an.
            await init_beanie(
                database=client.get_database("website_analyzer_db"), 
                document_models=[User, AnalysisJob]
            )
            
            print(f"✅ DB: Datenbankverbindung erfolgreich auf Versuch {attempt + 1}.")
            return # Wichtig: Die Funktion hier beenden, wenn erfolgreich
        
        except Exception as e:
            print(f"⚠️ DB: Datenbankverbindung fehlgeschlagen auf Versuch {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"   Warte {retry_delay} Sekunden...")
                await asyncio.sleep(retry_delay)
            else:
                print("🚨 DB: Konnte nach allen Versuchen keine Verbindung zur Datenbank herstellen.")
                raise # Den Fehler weiterwerfen, damit der Celery-Task als 'failed' markiert wird