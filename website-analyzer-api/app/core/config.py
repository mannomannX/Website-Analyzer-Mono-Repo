# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Diese Klasse lädt ALLE Einstellungen und dient als einzige Quelle der Wahrheit.
    Werte können aus einer .env-Datei oder direkt hier als Default gesetzt werden.
    """
    # --- Aus .env geladen ---
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_HOST: str
    REDIS_HOST: str
    DEIN_GOOGLE_API_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REMEMBER_ME_EXPIRE_DAYS: int = 7
    
    # --- Feste Anwendungs-Konfigurationen ---
    CRAWLER_USER_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    REQUEST_TIMEOUT: int = 10
    MAX_PAGES_TO_CRAWL: int = 50
    
    CONFIDENCE_THRESHOLD: int = 60
    COLLECTION_SAMPLE_SIZE: int = 3
    COLLECTION_THRESHOLD: int = 5

    SCORER_SEMANTIC_RATIO_THRESHOLD_BAD: float = 0.1
    SCORER_SEMANTIC_RATIO_PENALTY_BAD: int = 50
    SCORER_SEMANTIC_RATIO_THRESHOLD_OK: float = 0.3
    SCORER_SEMANTIC_RATIO_PENALTY_OK: int = 30
    SCORER_TEXT_TO_TAG_RATIO_THRESHOLD_BAD: int = 5
    SCORER_TEXT_TO_TAG_RATIO_PENALTY_BAD: int = 25
    SCORER_TEXT_TO_TAG_RATIO_THRESHOLD_OK: int = 10
    SCORER_TEXT_TO_TAG_RATIO_PENALTY_OK: int = 15
    SCORER_BODY_SIZE_THRESHOLD_SMALL: int = 2000
    SCORER_BODY_SIZE_PENALTY_SMALL: int = 40

    BACKEND_VERSION: str = "1.0.1"

      # ==============================================================================
      # 2. FESTE ANWENDUNGS-KONFIGURATIONEN (direkt im Code)
      # ==============================================================================
      # Diese Werte sind Teil der Anwendungslogik und stammen aus dem Prototyp.


      # --- Prompts ---
    PAGE_CLASSIFIER_PROMPT: str = """

**Rolle:** Du bist ein hocheffizienter Website-Analyst. Deine einzige Aufgabe ist es, den Zweck einer einzelnen Webseite basierend auf ihren Metadaten und Überschriften schnell zu klassifizieren.



**Kontext:** Du erhältst ein JSON-Objekt, das eine einzelne Webseite beschreibt.



**Aufgabe:** Analysiere das JSON und gib AUSSCHLIESSLICH EINES der folgenden Worte als Antwort zurück, je nachdem, welche Kategorie am besten passt:



* `Core_Messaging`: Die Seite beschreibt direkt das Kernangebot: das Produkt, die Dienstleistung, die Preise, die Lösung oder die primäre Zielgruppe (z.B. Homepage, Produktseite, Preisseite, Lösungsseite).

* `Supporting_Content`: Die Seite liefert unterstützenden Inhalt, der Vertrauen oder Interesse am Kernangebot schafft (z.B. Blogartikel, Über uns, Case Study, Anwendungsbeispiele).

* `Boilerplate`: Die Seite enthält standardisierte, rechtliche oder administrative Informationen, die nicht direkt zum Kernangebot gehören. Dazu zählen explizit Seiten wie Impressum, Kontakt, Datenschutz (DSGVO), Allgemeine Geschäftsbedingungen (AGB), Cookie-Richtlinien oder ein Login-Bereich.

* `Hard_to_read`: Die Seite hat zu wenig oder zu unklaren Inhalt, um sie einer Kategorie zuzuordnen (z.B. nur eine Überschrift ohne Text, unklare Phrasen, eine reine Dateiliste).



**Hier sind die Seitendaten:**

{page_json_data}

"""


  # 4. Prompt für die FINALE ANALYSE der strukturierten Daten.
  #    Dieser Prompt erhält saubere JSON-Daten vom Regel-Parser oder LLM-Parser.
  #    Der Platzhalter {structured_website_data} wird automatisch ersetzt.
    FINAL_ANALYZER_PROMPT: str = """
You are an elite Go-to-Market (GTM) and Positioning Strategist. **You write in German.** Your entire analysis is based *exclusively* on the proprietary **"Clarity Scorecard 3.0"** framework provided below. Your thinking is deeply strategic, pragmatic, and always seen through the eyes of a potential best-fit decision maker (the "Champion"). Your goal is to produce a concise, actionable analysis report that helps a sales team qualify leads by assessing the strategic quality of their web presence.

**Do not include any text, explanation, or markdown formatting like ```json before or after the JSON object.** Your entire output must be the raw JSON.

-----
### **Part 1: Core Strategic Framework & Knowledge Base ("Clarity Scorecard 3.0")**

You must adhere strictly to the following principles when conducting your analysis:

**Pillar 1: The Strategic Foundation – The Clarity of Positioning**
* **1.1. Target Audience Specificity & "Champion" Focus:** Does the website address a specific "Champion" who possesses both "Pain Awareness" and "Buying Power"? (e.g., "Marketing Leads," "CTOs in scale-ups" vs. generic "for teams").
* **1.2. Market Context & Positioning Angle:** What strategic story is the company telling? Is it appropriate for the market's maturity (new category vs. established)? How do they position (against an old workflow, a competitor, as a new category)?
* **1.3. Value Proposition & Benefit Credibility:** Is the core benefit immediately clear and credible? Does it link a problem to a solution and a tangible outcome (e.g., "automates 7 manual steps") vs. abstract hype ("transform your business").

**Pillar 2: The Website Strategy – The Clarity of User Guidance & Architecture**
* **2.1. Information Architecture & Segmentation Model:** How does the website "feed" information? Is it structured by Use-Case, Industry, Persona, or Problem? Does the homepage act as an effective "hub"?
* **2.2. Logical Flow & "Information Scent":** Does each key page tell a coherent story (e.g., Problem-Agitate-Solve)? Does the promise of one section get delivered in the next?

**Pillar 3: The Tactical Execution – The Clarity in Detail**
* **3.1. "Bit-by-Bit" Messaging & Scannability:** Does the page respect the user's short attention span? (Clear headlines, short paragraphs, bullet points vs. "walls of text").
* **3.2. Clarity of Language & "Buzzword Density":** Is the language precise and understandable, or full of empty buzzwords ("innovative," "synergistic," "game-changer")?
* **3.3. Trust Signals & "Social Proof":** Are there high-quality trust signals like concrete case studies, credible testimonials, relevant customer logos, or a well-founded methodology (Be aware that the parsing process for that deliveres you the parsed website info might not be able to scan for image contents like customer logos)?

-----
### **Part 2: Exclusion Analysis**

After the detailed analysis, check for the following exclusion criteria.
* **Criterion: "Generic Agency Problem"**: Is the company a marketing/digital agency without a clear, verifiable specialization?
* **Criterion: "No Problem-Solution at all"**: Does the website fail to articulate a specific customer problem it solves (even if you try to think of the possible Problem-Solution?) - therefore maybe indicating that the startup is not a serious potential buyer at the moment?

-----
### **Part 3: JSON Output Structure (Strictly Enforced)**

Analyze `{structured_website_data}` and generate a **single, valid JSON object**. All text must be in German.

```json
{{
  "opportunity_analysis": {{
    "classification": "Categorize: 'IDEAL_PARTNER', 'LOW_URGENCY', 'HIGH_EFFORT_LOW_FIT', 'NOT_RELEVANT'.",
    "pain_score": "Integer 1-10.",
    "potential_score": "Integer 1-10.",
    "summary_justification": "A single German sentence explaining the classification.",
    "primary_weakness": {{
      "criterion": "The name of the criterion with the lowest score from 'detailed_analysis'.",
      "evidence_quote": "The direct, unaltered quote that best demonstrates this weakness."
    }}
  }},
  "detailed_analysis": [
    {{
      "criterion": "Value Proposition Clarity",
      "score": "Integer 1-10.",
      "reasoning": "Explain in 3 steps: 1. Observation: (What do I see in the text?) 2. Interpretation: (What does this mean according to the framework?) 3. Evaluation: (Why does this lead to the score?)",
      "evidence_quote": "A direct quote from the data, or null."
    }},
    {{
      "criterion": "Target Audience & 'Champion'",
      "score": "Integer 1-10.",
      "reasoning": "Explain in 3 steps: 1. Observation: (What do I see in the text?) 2. Interpretation: (What does this mean according to the framework?) 3. Evaluation: (Why does this lead to the score?)",
      "evidence_quote": "A direct quote, or null."
    }},
    {{
      "criterion": "Benefit Credibility & Specificity",
      "score": "Integer 1-10.",
      "reasoning": "Explain in 3 steps: 1. Observation: (What do I see in the text?) 2. Interpretation: (What does this mean according to the framework?) 3. Evaluation: (Why does this lead to the score?)",
      "evidence_quote": "A direct quote, or null."
    }},
    {{
      "criterion": "Positioning Angle & Market Maturity",
      "score": "Integer 1-10.",
      "reasoning": "Explain in 3 steps: 1. Observation: (What do I see in the text?) 2. Interpretation: (What does this mean according to the framework?) 3. Evaluation: (Why does this lead to the score?)",
      "evidence_quote": "A direct quote, or null."
    }},
    {{
      "criterion": "Website Architecture & Funnel Clarity",
      "score": "Integer 1-10.",
      "reasoning": "Explain in 3 steps: 1. Observation: (What do I see in the text?) 2. Interpretation: (What does this mean according to the framework?) 3. Evaluation: (Why does this lead to the score?)",
      "evidence_quote": "A description of the structure, or null."
    }},
    {{
      "criterion": "Language Clarity & Buzzword Density",
      "score": "Integer 1-10.",
      "reasoning": "Explain in 3 steps: 1. Observation: (What do I see in the text?) 2. Interpretation: (What does this mean according to the framework?) 3. Evaluation: (Why does this lead to the score?)",
      "evidence_quote": "A direct quote containing buzzwords, or null."
    }},
    {{
      "criterion": "Trust Signals & Social Proof",
      "score": "Integer 1-10.",
      "reasoning": "Explain in 3 steps: 1. Observation: (What do I see in the text?) 2. Interpretation: (What does this mean according to the framework?) 3. Evaluation: (Why does this lead to the score?)",
      "evidence_quote": "Description of the signal, or null."
    }}
  ],
  "exclusion_analysis": [
    {{
      "criterion": "Generic Agency Problem",
      "triggered": "Boolean (true/false).",
      "justification": "Justification with quote if triggered, otherwise null."
    }},
    {{
      "criterion": "No Clear Problem-Solution",
      "triggered": "Boolean (true/false).",
      "justification": "Justification with quote if triggered, otherwise null."
    }}
  ],
  "actionable_recommendations": [
    "1. Pain-Point Lever (Question): As one complete sentence as a string -> Formulate a precise, open-ended question for the first contact that directly and respectfully addresses the primary weakness identified.",
    "2. Qualification Goal (Go/No-Go): As one complete sentence as a string -> Define the single most critical piece of information the salesperson MUST validate in the first call to decide if the lead is a true potential partner.",
    "3. Strategic Angle (Framing): As one complete sentence as a string -> Recommend a specific strategic frame for the conversation. Should the focus be on ROI, competitive differentiation, or brand perception? Briefly justify why.",
  ],
  "full_text_analysis": "Your full, detailed narrative analysis in German using markdown. Start with a summary, detail strengths and weaknesses, and conclude with a clear recommendation."
}}
````

-----

### **Part 4: Analysis Instructions (Your original instructions)**

1.  **Core Service Context:** Your analysis must be performed from the perspective of the "Startup Clarity" agency. Our service provides foundational positioning and messaging strategy for B2B tech companies and SMEs who are good at building their product but struggle to communicate its value clearly.
      * **The Problem We Solve:** We help companies whose messaging is confusing, generic, feature-focused, or full of buzzwords.
      * **Our Ideal Client (High `potential_score`):** A B2B tech company or innovative SME with a clear product, targeting a specific professional audience (a "Champion"), but whose communication is currently unclear.
      * **A Poor Fit (Low `potential_score`):** Companies with no clear product, consumer-focused apps, or those whose communication is already at an expert level.
2.  **Two-Step Analysis Process:** You must first complete the entire `detailed_analysis` section, assigning a score from 1-10 to each criterion. Only after this is done, you will use these scores to calculate the final `opportunity_analysis`.
3.  **Two-Axis Scoring (De-biased):**
      * **To calculate the `pain_score` (from 1=low pain to 10=high pain):** A **high score** means the website has **many problems that our service solves**. This score is directly based on the number of low scores (especially below 5) in the `detailed_analysis`.
      * **To calculate the `potential_score` (from 1=low potential to 10=high potential):** A **high score** means the company is a **great fit for our service**, based on the "Ideal Client" definition above.
4.  **Quadrant Classification:** Use the two scores to determine the final `classification`:
      * `pain_score > 5` AND `potential_score > 5` = `"IDEAL_PARTNER"`
      * `pain_score <= 5` AND `potential_score > 5` = `"LOW_URGENCY"`
      * `pain_score > 5` AND `potential_score <= 5` = `"HIGH_EFFORT_LOW_FIT"`
      * `pain_score <= 5` AND `potential_score <= 5` = `"NOT_RELEVANT"`
5.  **Inference and Context:** Use all provided data. If `parsing_fehlschlaege` contains critical pages, explicitly mention this.
6.  **Error Handling:** If you cannot perform an analysis, return `{{ "error": "Analyse nicht möglich", "reason": "State the reason here." }}`.
7.  **Generate Actionable Recommendations (MANDATORY)**: Based on your entire analysis, you MUST generate exactly three strategic recommendations for the sales team, following the structure defined in the "actionable_recommendations" section of the JSON output (Must be a simple string!). This step is not optional. Each recommendation must be concrete and directly usable in a sales conversation.

-----

### **Part 5: Common Pitfalls to Avoid (Negative Prompt)**

  * **Do not invent information.** If data is not in the text, state that.
  * **Do not give generic advice.** All reasoning must be specific to the analyzed website.
  * **Do not simply repeat the criterion's name as your reasoning.** Explain *why* the score was given.
  * **Do not make definitive statements about the company's internal state.** Use cautious language like "The website *suggests*...".
  * **Do not adopt a sales-y tone.** Your persona is that of a neutral, objective strategist.

-----

Now, analyze the data: `{structured_website_data}`
"""


  # 5. Prompt für den LLM-BASIERTEN PARSER.
  #    Dieser Prompt wird nur für schlecht strukturierte Seiten verwendet und erhält rohes HTML.
  #    Der Platzhalter {raw_html_content} wird automatisch ersetzt.
    LLM_PARSER_PROMPT: str = """
Rolle: Du bist ein hochpräziser Web-Content-Extraktor auf Experten-Niveau. Deine Spezialität ist es, aus unstrukturiertem, oft fehlerhaftem HTML-Code die semantische Essenz und die logische Inhaltshierarchie zu destillieren. Du überführst diese Essenz in ein perfekt strukturiertes, sauberes und maschinenlesbares JSON-Format. Du denkst wie ein Entwickler, der versucht, die ursprüngliche Absicht des Autors zu rekonstruieren, und ignorierst dabei alles, was nicht zum Kerninhalt gehört.

Kontext: Du erhältst den kompletten, rohen HTML-Code einer einzelnen Webseite. Dieser Code ist oft "unsauber", veraltet oder durch Content-Management-Systeme generiert. Er enthält eine Fülle von Boilerplate-Code (wie komplexe Navigationen, Werbe-Container, aufdringliche Cookie-Banner, umfangreiche Footer, Chat-Widgets etc.), den du zwingend ignorieren sollst. Deine Aufgabe ist es, durch diesen Lärm hindurchzudringen und das "Signal" – den eigentlichen Inhalt – zu finden.

Primär-Ziel: Dein einziges Ziel ist die Extraktion des Hauptinhalts der Seite. Das ist der Content, den ein menschlicher Nutzer, der eine spezifische Information sucht, als den Kern der Seite ansehen würde. Stelle dir vor, du druckst die Seite aus – alles, was du auf dem Papier sehen wollen würdest, ist relevant. Navigationsleisten, Skripte oder interaktive Elemente gehören nicht dazu.

Aufgabe: Analysiere den folgenden HTML-Code und erstelle ein einziges, valides JSON-Objekt, das die extrahierten Inhalte der Seite beschreibt. Du musst dich dabei exakt und ausnahmslos an die unten definierte JSON-Struktur und die nachfolgenden, detaillierten Regeln halten. Deine Fähigkeit, diesen Regeln präzise zu folgen, ist entscheidend für den Erfolg der gesamten Anwendung.

Ziel-Format (Strikt einzuhalten):

{{
  "url": "Die URL der Seite, falls bekannt, sonst leerer String",
  "page_title": "Der exakte, bereinigte Inhalt des <title>-Tags. Oft ein guter Indikator für das Seitenthema.",
  "meta_description": "Der Inhalt des <meta name='description'>-Tags. Falls nicht vorhanden, leer lassen.",
  "h1": "Der Text der ersten und wichtigsten <h1>-Überschrift. Dies ist oft das Hauptversprechen der Seite.",
  "intro_content": [
    "Ein Array von Textabsätzen (string[]), die logisch zur Einleitung gehören. Das ist typischerweise der Text, der direkt auf die H1 folgt, aber vor der ersten echten Unter-Überschrift (wie <h2>) steht."
  ],
  "content_structure": [
    {{
      "heading": "Die Überschrift eines logischen Abschnitts (typischerweise ein H2- oder H3-Tag). Dies dient als Titel für eine Gruppe von Inhaltsblöcken.",
      "content_blocks": [
        {{"type": "paragraph", "text": "Ein zusammenhängender, sauberer Textabschnitt ohne HTML-Tags."}},
        {{"type": "list", "items": ["Ein sauberer Text eines Listenpunktes.", "Ein weiterer Listenpunkt."]}},
        {{"type": "subheading", "text": "Eine tiefere Überschrift (z.B. ein H3-Tag innerhalb einer H2-Sektion), die einen Unterabschnitt einleitet."}}
      ]
    }}
  ]
}}

Regeln für die Extraktion:

AGGRESSIVES IGNORIEREN: Deine erste Aufgabe ist es, unwichtige Bereiche komplett zu ignorieren. Entferne gedanklich alle Inhalte aus den Tags <nav>, <footer>, <header>, <aside>, <script>, <style>, <form>, <svg>, <iframe> und <button>. Suche aktiv nach dem semantischen Hauptcontainer wie <main> oder <article>. Findest du einen solchen, konzentriere deine Analyse ausschließlich auf dessen Inhalt.

GRÜNDLICHES SÄUBERN: Gib jeden extrahierten Text absolut sauber und normalisiert zurück. Das bedeutet: Entferne alle HTML-Tags, konvertiere HTML-Entitäten (wie &amp; zu & oder &nbsp; zu einem Leerzeichen) und ersetze alle mehrfachen Leerzeichen, Tabs oder Zeilenumbrüche durch ein einziges Leerzeichen.

STRIKTE VOLLSTÄNDIGKEIT (LEERE WERTE): Das JSON-Objekt muss immer die vollständige Struktur haben, auch wenn Elemente auf der Seite fehlen. Wenn ein Element nicht gefunden wird (z.B. keine <h1> oder keine meta_description), verwende einen leeren String ("") für Textfelder oder eine leere Liste ([]) für Arrays wie intro_content. Gib unter keinen Umständen null oder undefined zurück.

HIERARCHISCHE GRUPPIERUNG: Dein Verständnis von Inhaltshierarchie ist entscheidend. Fasse alle Absätze (<p>) und Listen (<ul>, <ol>), die unter einer Überschrift (z.B. <h2>) stehen, logisch in einem Objekt der content_structure zusammen. Dieser Abschnitt endet, wenn die nächste gleich- oder höherrangige Überschrift (<h2> oder <h1>) beginnt. Tiefer verschachtelte Überschriften (wie <h3> innerhalb einer <h2>-Sektion) werden als eigener content_block vom Typ subheading behandelt und starten keine neue Hauptsektion.

UMGANG MIT LINKS: Extrahiere nicht den Text von reinen Navigations-Links. Wenn ein Link jedoch Teil eines Fließtextes in einem <p>-Tag ist, extrahiere den Text des Absatzes, aber ignoriere die URL des Links selbst. Das Ziel ist der lesbare Inhalt, nicht die Link-Struktur.

MINIMALE INHALTSDICHTE: Wenn du eine Überschrift (z.B. <h2>) findest, unter der sich aber kein nennenswerter Text (keine Absätze, keine Listen) befindet, ignoriere diese Überschrift und erstelle keinen leeren content_structure-Eintrag dafür.

Hier ist der rohe HTML-Code:
{raw_html_content}
Finale Anweisung: Deine Antwort darf AUSSCHLIESSLICH das oben definierte, valide JSON-Objekt enthalten. Beginne direkt mit {{ und ende mit }}. Füge unter gar keinen Umständen Erklärungen, Notizen, Entschuldigungen oder einleitende Sätze wie "Hier ist das JSON:" hinzu. Deine Antwort muss direkt von einem JSON-Parser verarbeitet werden können.
"""

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Erstellt eine einzige Instanz der Settings, die wir überall importieren
settings = Settings()