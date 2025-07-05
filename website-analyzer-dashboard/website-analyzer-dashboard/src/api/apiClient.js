// src/api/apiClient.js

// Die Basis-URL unserer Backend-API.
// Sie wird aus einer Umgebungsvariable geladen, um flexibel zu bleiben.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Eine zentrale Funktion, um API-Anfragen zu senden.
 * Sie kümmert sich automatisch um Header und Fehlerbehandlung.
 */
async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Wenn die Antwort leer ist (z.B. bei Status 204 No Content), geben wir null zurück
    const responseText = await response.text();
    return responseText ? JSON.parse(responseText) : null;
}


/**
 * Loggt einen Benutzer ein und gibt das JWT-Token zurück.
 * @param {string} email - Die E-Mail des Benutzers.
 * @param {string} password - Das Passwort des Benutzers.
 * @returns {Promise<object>} Das Token-Objekt.
 */
export const login = async (email, password) => {
    // FastAPI's OAuth2PasswordRequestForm erwartet die Daten in einem speziellen Format (form-data),
    // nicht als JSON. Deshalb bauen wir es hier manuell zusammen.
    const formData = new URLSearchParams();
    formData.append('username', email); // Das Feld muss 'username' heißen
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Login failed with status: ${response.status}`);
    }

    return response.json();
};

// Hier werden wir später weitere API-Funktionen hinzufügen, z.B.:
// export const startAnalysis = async (url, token) => { ... }
// export const getJobStatus = async (jobId, token) => { ... }