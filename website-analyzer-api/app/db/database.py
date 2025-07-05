# app/db/database.py

import motor.motor_asyncio
from beanie import init_beanie
from app.core.config import settings
from app.db.models import User, AnalysisJob # Importiert unsere Modelle
import asyncio

# Globale Variable für den DB-Client
client = None

async def init_db():
    """
    Initialisiert die Datenbankverbindung und Beanie.
    Diese Funktion wird jetzt von beiden, API und Worker, aufgerufen.
    """
    global client
    print("--- DB: Initialisiere Datenbankverbindung... ---")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Verbindungsstring erstellen
            mongo_uri = f"mongodb://{settings.MONGO_INITDB_ROOT_USERNAME}:{settings.MONGO_INITDB_ROOT_PASSWORD}@{settings.MONGO_HOST}:27017"
            
            # Client erstellen (nur wenn er noch nicht existiert)
            if client is None:
                client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            
            # Verbindung pingen
            await client.admin.command('ping') 
            
            # Beanie mit allen Dokumenten initialisieren
            await init_beanie(database=client.website_analyzer_db, document_models=[User, AnalysisJob])
            
            print(f"✅ DB: Datenbankverbindung erfolgreich auf Versuch {attempt + 1}.")
            return
        
        except Exception as e:
            print(f"⚠️ DB: Datenbankverbindung fehlgeschlagen auf Versuch {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"   Warte {retry_delay} Sekunden...")
                await asyncio.sleep(retry_delay)
            else:
                print("🚨 DB: Konnte nach allen Versuchen keine Verbindung zur Datenbank herstellen.")
                raise