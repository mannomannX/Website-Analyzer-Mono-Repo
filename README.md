# 🤖 MonoMono Fusions-Repo

## 🗺️ Projekt-Map
### 🧩 Komponenten
- **[website-analyzer-dashboard](./website-analyzer-dashboard)** (Original: [mannomannX/website-analyzer-dashboard](https://github.com/mannomannX/website-analyzer-dashboard))
- **[website-analyzer-api](./website-analyzer-api)** (Original: [mannomannX/website-analyzer-api](https://github.com/mannomannX/website-analyzer-api))

### 🌳 Verzeichnisstruktur


```
Website-Analyzer-Mono-Repo/
├── .github/
│   └── workflows/
│       └── sync.yml             # GitHub Actions Workflow zur Synchronisierung
├── README.md                    # Diese Datei
├── website-analyzer-api/        # Backend-Dienst (FastAPI)
│   ├── .github/
│   │   └── workflows/
│   │       └── monomono-trigger.yml # Workflow für das API-Subprojekt
│   ├── .gitignore               # Git-Ignore-Regeln für das API-Backend
│   ├── app/                     # Hauptanwendungslogik
│   │   ├── api/                 # API-Endpunkte und Abhängigkeiten
│   │   │   ├── dependencies.py  # Abhängigkeiten für API-Routen
│   │   │   └── routes/          # Definition der API-Routen
│   │   │       ├── admin.py     # Admin-spezifische Routen
│   │   │       ├── analysis.py  # Routen für die Analyse
│   │   │       └── auth.py      # Authentifizierungs-Routen
│   │   ├── core/                # Kernlogik und Geschäftsregeln
│   │   │   ├── analyzer.py      # Website-Analyse-Logik
│   │   │   ├── confidence_scorer.py # Logik zur Vertrauensbewertung
│   │   │   ├── config.py        # Anwendungskonfiguration
│   │   │   ├── crawler.py       # Web-Crawler-Logik
│   │   │   ├── page_classifier.py # Klassifizierung von Webseiten
│   │   │   ├── parser.py        # HTML-Parsing-Logik
│   │   │   └── security.py      # Sicherheitsfunktionen (z.B. JWT)
│   │   ├── db/                  # Datenbank-Modelle und -Verbindungen
│   │   │   ├── database.py      # Datenbankverbindung und -Sitzungen
│   │   │   └── models.py        # SQLAlchemy-Modelle
│   │   ├── main.py              # Haupt-FastAPI-Anwendung
│   │   ├── schemas/             # Pydantic-Schemas für Datenvalidierung
│   │   │   ├── analysis.py      # Schemas für Analysedaten
│   │   │   ├── token.py         # Schemas für Token (JWT)
│   │   │   └── user.py          # Schemas für Benutzerdaten
│   │   └── worker/              # Celery Worker für Hintergrundaufgaben
│   │       ├── celery_app.py    # Celery-Anwendungskonfiguration
│   │       └── tasks.py         # Definition der Celery-Aufgaben
│   ├── docker-compose.yml       # Docker Compose für Entwicklung/Deployment
│   ├── Dockerfile               # Dockerfile für die FastAPI-Anwendung
│   ├── Dockerfile.worker        # Dockerfile für den Celery Worker
│   ├── README.md                # Spezifische README für das API-Backend
│   ├── requirements.txt         # Python-Abhängigkeiten
│   └── scripts/
│       └── create_admin_user.py # Skript zur Erstellung eines Admin-Benutzers
└── website-analyzer-dashboard/  # Frontend-Anwendung (React)
    ├── .github/
    │   └── workflows/
    │       └── monomono-trigger.yml # Workflow für das Dashboard-Subprojekt
    └── website-analyzer-dashboard/  # Tatsächliches Dashboard-Verzeichnis
        ├── .gitignore           # Git-Ignore-Regeln für das Dashboard
        ├── eslint.config.js     # ESLint-Konfiguration
        ├── index.html           # Haupt-HTML-Datei
        ├── package-lock.json    # Lock-Datei für npm-Pakete
        ├── package.json         # Projektinformationen und Abhängigkeiten (npm)
        ├── public/
        │   └── vite.svg         # Vite-Logo
        ├── README.md            # Spezifische README für das Dashboard
        ├── src/                 # Quellcode des React-Dashboards
        │   ├── api/
        │   │   └── apiClient.js # API-Client für die Kommunikation mit dem Backend
        │   ├── App.css          # Globale CSS-Datei
        │   ├── App.jsx          # Haupt-React-Komponente
        │   ├── assets/
        │   │   └── react.svg    # React-Logo
        │   ├── index.css        # Index-CSS-Datei
        │   ├── main.jsx         # Einstiegspunkt der React-Anwendung
        │   └── pages/
        │       └── LoginPage.jsx # Login-Seite
        └── vite.config.js       # Vite-Konfigurationsdatei
```

> Letzte Aktualisierung: Thu Jul 10 14:50:07 UTC 2025
