# Notebook für Studierende

Damit das Notebook laeuft, muessen diese Dateien zusammen im selben Ordner bleiben:

- `teaching_dash_minimal.ipynb`
- `teaching_dash_minimal_utils.py`
- `main_api.py`
- `requirements.txt`
- `start_notebook_env.sh`

## Warum sind `main_api.py` und `teaching_dash_minimal_utils.py` noetig?

Das Notebook importiert das lokale Modul `teaching_dash_minimal_utils`.
Dieses Modul nutzt wiederum `main_api.py` fuer die SEC-Company-Facts-Logik.
Python findet diese Module nur, wenn sich beide Dateien im gleichen Projektordner befinden oder dieser Ordner im `PYTHONPATH` liegt.

## Spaetere GitHub-Variante fuer `main_api`

Wenn `main_api` spaeter als eigenes GitHub-Repo veroeffentlicht wird, kann das Lehrprojekt auf zwei Arten genutzt werden:

### Aktuelle, robuste Lehrvariante

- `main_api.py` liegt lokal im gleichen Ordner wie das Notebook.
- Diese Variante ist fuer Studierende am stabilsten.

### Spaetere Paket-Variante ueber GitHub

- `main_api.py` wird durch ein installiertes Python-Paket ersetzt.
- In `requirements.txt` kann dann ein GitHub-Eintrag wie dieser aktiviert werden:

```bash
pip install git+https://github.com/DEINNAME/main_api.git@v0.1.0
```

- Fuer Lehrveranstaltungen sollte dabei immer eine feste Version wie `v0.1.0` verwendet werden.
- Ohne feste Version kann sich das Verhalten mitten im Semester unbeabsichtigt aendern.

## Schnellstart

### macOS / Linux

```bash
chmod +x start_notebook_env.sh
./start_notebook_env.sh
```

Das Skript:

- erstellt bei Bedarf automatisch ein lokales `.venv`
- installiert die benoetigten Pakete aus `requirements.txt`
- setzt den Projektordner in den `PYTHONPATH`
- startet JupyterLab direkt mit dem Notebook

## Manuelle Alternative

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m jupyter lab teaching_dash_minimal.ipynb
```

## Wichtige Hinweise fuer die Abgabe an Studierende

- Nicht nur das Notebook verschicken, sondern immer den ganzen Ordner oder mindestens die fuenf Dateien oben.
- Das Notebook erwartet Internetzugriff fuer SEC API und optional fuer OpenRouter.
- Fuer LLM-Funktionen brauchen Studierende einen eigenen `OPENROUTER_API_KEY`.
- Wenn der Import fehlschlaegt, liegt fast immer `teaching_dash_minimal_utils.py` oder `main_api.py` nicht im gleichen Ordner.
- Wenn spaeter auf die GitHub-Variante umgestellt wird, sollte die lokale `main_api.py` aus dem Lehrprojekt entfernt oder bewusst durch die Paket-Version ersetzt werden, damit es keine Mehrdeutigkeit gibt.
