# Website Analyzer API

Dies ist das Backend-System für den Website Analyzer. Es ist als service-orientierte Architektur aufgebaut und dient als zentrales Gehirn für die Annahme, Verarbeitung und Speicherung von Website-Analysen.

## Architektur-Übersicht

Das Gesamtsystem besteht aus drei separaten Repositories:

1.  **`website-analyzer-api` (Dieses Repo):** Das Herzstück. Eine in Python geschriebene API, die auf FastAPI basiert. Sie ist verantwortlich für:
    * Benutzer-Authentifizierung (Login, Token-Erstellung).
    * Annahme von Analyse-Aufträgen über eine API-Schnittstelle.
    * Delegation der langwierigen Analyse-Aufgaben an einen Hintergrund-Worker.
    * Speicherung und Abruf von Ergebnissen aus der MongoDB-Datenbank.

2.  **`website-analyzer-dashboard`:** Eine Frontend-Webanwendung (z.B. in React oder Vue.js), die als zentrale Kommandozentrale für die Mitarbeiter dient. Hier können alle Analyseergebnisse eingesehen und neue Nutzer von Admins verwaltet werden.

3.  **`website-analyzer-extension`:** Eine schlanke Browser-Erweiterung, die als "Hot-Key" dient, um schnell und einfach die URL der aktuell besuchten Seite zur Analyse-Warteschlange hinzuzufügen.

![Architektur-Diagramm](https://i.imgur.com/YwK71Wn.png)

## Technologie-Stack

* **Backend-Framework:** FastAPI
* **Asynchrone Tasks:** Celery
* **Datenbank:** MongoDB
* **Message Broker (für Celery):** Redis
* **Containerisierung:** Docker & Docker Compose
* **Authentifizierung:** JWT (JSON Web Tokens)
* **Datenbank-Client (Python):** Beanie (Pydantic-basiert)

---

## Lokale Entwicklungsumgebung aufsetzen

### Voraussetzungen

* Docker
* Docker Compose

### Schritte

1.  **Repository klonen:**
    ```bash
    git clone [URL_dieses_Repos]
    cd website-analyzer-api
    ```

2.  **Umgebungsvariablen erstellen:**
    * Kopieren Sie die Vorlagedatei `.env.example` zu einer neuen Datei namens `.env`.
    * ```bash
      cp .env.example .env
      ```
    * Öffnen Sie die `.env`-Datei und tragen Sie Ihre "Geheimnisse" ein, insbesondere Ihren `DEIN_GOOGLE_API_KEY` und einen beliebigen `JWT_SECRET_KEY`. Die MongoDB- und Redis-Werte können für die lokale Entwicklung so belassen werden.

3.  **Container starten:**
    * Führen Sie den folgenden Befehl im Hauptverzeichnis aus. Er baut die Docker-Images und startet alle vier Dienste (API, Worker, MongoDB, Redis).
    * ```bash
      docker-compose up --build
      ```
    * Die API ist jetzt unter `http://localhost:8000` erreichbar.

4.  **Ersten Admin-Benutzer erstellen:**
    * Öffnen Sie ein **zweites, neues Terminal**.
    * Starten Sie eine interaktive Kommandozeile im laufenden API-Container:
        ```bash
        docker-compose exec api bash
        ```
    * Führen Sie das Skript zur Erstellung des Admin-Nutzers aus:
        ```bash
        python /scripts/create_admin_user.py
        ```
    * Folgen Sie den Anweisungen, um eine E-Mail und ein Passwort für Ihren ersten Admin-Account festzulegen.

5.  **API testen:**
    * Öffnen Sie Ihren Browser und gehen Sie zur interaktiven Dokumentation unter `http://localhost:8000/docs`.
    * Nutzen Sie den `/auth/login`-Endpunkt, um sich mit Ihren Admin-Daten einzuloggen und ein JWT-Token zu erhalten.

---

## Nächste Schritte

Nachdem das Backend läuft, können die Frontend-Projekte (`website-analyzer-dashboard` und `website-analyzer-extension`) entwickelt werden, die auf diese API zugreifen.